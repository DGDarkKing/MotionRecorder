import datetime
from queue import Queue

import cv2

from capturer import VideoCapturer
from motion_recorders.motion_recorder import MotionRecorder


class BatchMonotimeMotionRecorder(MotionRecorder):
    def __init__(
            self,
            video_paths: Queue,
            create_output_name_delegate,
            kernel,
            area_of_interesting,
            cap_fps_movement,
            threshold,
            output_time_limit: datetime.timedelta,

    ):
        super().__init__(video_paths.get(), create_output_name_delegate(), kernel, area_of_interesting,
                         cap_fps_movement,
                         threshold)
        self._video_paths = video_paths
        self._output_time_limit = output_time_limit
        self._create_output_name_delegate = create_output_name_delegate
        self._writen_frame_number = 0
        self._output_video_fps = None

    def record(self):
        self._io_init()
        self._dependency_io_init()
        _, src_frame_t_minus, translated_frame_t_minus = self._read_first_checked_frame()
        _, src_frame_t, translated_frame_t = self._read_checked_frame()

        while not self._is_end_video:
            _, src_frame_t_plus, translated_frame_t_plus = self._read_checked_frame()
            if self._is_end_video:
                break
            mask_frame, mean_of_mask = self._difference_image(translated_frame_t_minus, translated_frame_t,
                                                              translated_frame_t_plus)
            if is_motion := mean_of_mask > self._threshold:
                foreground_frame = translated_frame_t_minus
                translated_frame_t_minus, translated_frame_t = translated_frame_t, translated_frame_t_plus
                self._write(src_frame_t_plus)
                while is_motion and not self._is_end_video:
                    _, src_frame_t_plus = self._read()
                    if self._is_end_video:
                        break
                    if self._frame_number % self._required_frame_number != 0:
                        self._write(src_frame_t_plus)
                        continue
                    translated_frame_t_plus = self.translate_frame(src_frame_t_plus)
                    mask_frame, mean_of_mask = self._difference_image(translated_frame_t_minus, translated_frame_t,
                                                                      translated_frame_t_plus)
                    is_motion = mean_of_mask > self._threshold
                    if is_motion:
                        self._write(src_frame_t_plus)
                    else:
                        mask_frame, mean_of_mask = self._difference_image(foreground_frame, translated_frame_t,
                                                                          translated_frame_t_plus)
                        is_motion = mean_of_mask > self._threshold
                        if is_motion:
                            self._write(src_frame_t_plus)
                    translated_frame_t_minus, translated_frame_t = translated_frame_t, translated_frame_t_plus
            else:
                translated_frame_t_minus, translated_frame_t = translated_frame_t, translated_frame_t_plus
        self._release()

    def _io_init(self):
        super()._io_init()
        self._output_video_fps = self._video_reader.fps

    def _write(self, frame):
        self._video_writer.write(frame)
        self._writen_frame_number += 1
        if self._writen_frame_number > self._output_time_limit.seconds * self._output_video_fps:
            self._video_writer.release()
            fps, width, height = self._video_reader.fps, self._video_reader.width, self._video_reader.height
            self._output_path = self._create_output_name_delegate()
            self._video_writer = cv2.VideoWriter(self._output_path, self.FOURCC, fps, (width, height))
            self._output_video_fps = fps
            self._writen_frame_number = 0

    def _read(self):
        retval, frame = self._video_reader.read()
        self._frame_number += 1
        if not retval:
            if self._open_next_video():
                return self._read()
            self._is_end_video = not retval
            return retval, None
        return retval, frame

    def _read_checked_frame(self):
        while (retval := self._video_reader.grab()) and self._frame_number % self._required_frame_number:
            self._frame_number += 1
        if not retval:
            if self._open_next_video():
                return self._read_checked_frame()
            self._is_end_video = not retval
            return False, None, None
        retval, frame = self._video_reader.retrieve()
        self._frame_number += 1
        translated_frame = self.translate_frame(frame)
        return retval, frame, translated_frame

    def _open_next_video(self):
        if self._video_paths.empty():
            return False
        self._video_reader.release()
        self._video_path = self._video_paths.get()
        self._video_reader = VideoCapturer(self._video_path)
        return True


