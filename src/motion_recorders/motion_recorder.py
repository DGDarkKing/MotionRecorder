import cv2

from capturer import VideoCapturer


class MotionRecorder:
    CODEC = 'mp4v'

    def __init__(
            self,
            video_path,
            output_path,
            kernel,
            area_interest,
            cap_fps_movement,
            threshold
    ):
        self._video_reader: VideoCapturer = None
        self._video_writer = None
        self._required_frame_number = None

        self._kernel = kernel
        self._area_interest = area_interest
        self._threshold = threshold
        self._frame_number = 0
        self._is_end_video = False
        self._video_path = video_path
        self._output_path = output_path
        self._cap_fps_movement = cap_fps_movement

    def record(self):
        self._io_init()
        self._io_dependency_init()
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
                self._video_writer.write(src_frame_t_plus)
                while is_motion and not self._is_end_video:
                    _, src_frame_t_plus = self._read()
                    if self._is_end_video:
                        break
                    if self._frame_number % self._required_frame_number != 0:
                        self._video_writer.write(src_frame_t_plus)
                        continue
                    translated_frame_t_plus = self.translate_frame(src_frame_t_plus)
                    mask_frame, mean_of_mask = self._difference_image(translated_frame_t_minus, translated_frame_t,
                                                                      translated_frame_t_plus)
                    is_motion = mean_of_mask > self._threshold
                    if is_motion:
                        self._video_writer.write(src_frame_t_plus)
                    else:
                        mask_frame, mean_of_mask = self._difference_image(foreground_frame, translated_frame_t,
                                                                          translated_frame_t_plus)
                        is_motion = mean_of_mask > self._threshold
                        if is_motion:
                            self._video_writer.write(src_frame_t_plus)
                    translated_frame_t_minus, translated_frame_t = translated_frame_t, translated_frame_t_plus
            else:
                translated_frame_t_minus, translated_frame_t = translated_frame_t, translated_frame_t_plus

        self._release()

    def _read(self):
        retval, frame = self._video_reader.read()
        self._frame_number += 1
        self._is_end_video = not retval
        return retval, frame

    def _read_first_checked_frame(self):
        retval, frame, translated_frame = self._read_checked_frame()
        return retval, frame, translated_frame

    def _read_checked_frame(self):
        while (is_not_end_video := self._video_reader.grab()) and self._frame_number % self._required_frame_number:
            self._frame_number += 1
        self._is_end_video = not is_not_end_video
        if self._is_end_video:
            return False, None, None
        retval, frame = self._video_reader.retrieve()
        self._frame_number += 1
        translated_frame = self.translate_frame(frame)
        return retval, frame, translated_frame

    def _io_init(self):
        self._video_reader = VideoCapturer(self._video_path)
        fourcc = cv2.VideoWriter_fourcc(*self.CODEC)
        fps, width, height = self._video_reader.fps, self._video_reader.width, self._video_reader.height
        self._video_writer = cv2.VideoWriter(self._output_path, fourcc, fps, (width, height))

    def _io_dependency_init(self):
        self._required_frame_number = self._video_reader.fps // self._cap_fps_movement

    def _difference_image(self, frame_t_minus, frame_t, frame_t_plus):
        delta_t_plus = cv2.absdiff(frame_t_plus, frame_t)
        delta_t = cv2.absdiff(frame_t, frame_t_minus)
        mask_frame = cv2.bitwise_and(delta_t_plus, delta_t)
        mask_frame = cv2.morphologyEx(mask_frame, cv2.MORPH_OPEN, self._kernel)
        return mask_frame, mask_frame.mean()

    def translate_frame(self, frame):
        frame = frame[
                self._area_interest[0][1]:self._area_interest[1][1],
                self._area_interest[0][0]:self._area_interest[1][0]
                ]
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def _release(self):
        self._video_writer.release()
        self._video_reader.release()
