import datetime
import json
import os.path
from queue import Queue

import cv2

from motion_recorders.batch_monotime_recorder import BatchMonotimeMotionRecorder

# video_dir = os.environ['VideoDir']
video_dir = 'media'
video_names = os.environ['VideoNames']
print(video_names)
video_names = json.loads(video_names)

# video_names = ['firstMonotimeTest.mp4', 'secondMonotimeTest.mp4']
video_paths = Queue()
for video_name in video_names:
    path = os.path.join(video_dir, video_name)
    print(path)
    video_paths.put(path)
output_path = 'render'
#                       left_top    bottom_right
# interesting_area = [(x_lt, y_lt), (x_br, y_br)]
area_interest = json.loads(os.environ['AreaInterest'])
print(area_interest)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
cap_fps = 5
threshold = 0.5

def calc_name():
    return os.path.join(output_path, f'test_result {datetime.datetime.now().strftime("%H-%M-%S.%f")}.mp4')

motion_recorder = BatchMonotimeMotionRecorder(video_paths, calc_name, kernel, area_interest, cap_fps, threshold,
                                              datetime.timedelta(hours=1))
try:
    motion_recorder.record()
except Exception as e:
    pass
#
#
#
#
#
#
#
#
#
#

#
#
#


# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
# required_frame_num = fps // cap_fps
#
# _, src_pivot = video_reader.read()
# pivot = translate_frame(src_pivot, interesting_area)
# frame_number = 0
# while frame_number <= required_frame_num:
#     video_reader.grab()
#     frame_number += 1
# _, src_frame_t = video_reader.retrieve()
# frame_t = translate_frame(src_frame_t, interesting_area)
#
# while video_reader.grab():
#     frame_number += 1
#     if frame_number % required_frame_num != 0:
#         continue
#     _, src_frame = video_reader.retrieve()
#     frame = translate_frame(src_frame, interesting_area)
#     mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)
#
#     if is_motion := mean_of_mask > threshold:
#         foreground = pivot
#         pivot = frame_t
#         frame_t = frame
#         video_writer.write(src_frame)
#         while is_motion and video_reader.grab():
#             frame_number += 1
#             _, src_frame = video_reader.retrieve()
#             if frame_number % required_frame_num != 0:
#                 video_writer.write(src_frame)
#                 continue
#             frame = translate_frame(src_frame, interesting_area)
#             mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)
#             is_motion = mean_of_mask > threshold
#             if is_motion:
#                 video_writer.write(src_frame)
#             else:
#                 mask_frame, mean_of_mask = diffImage(foreground, frame_t, frame, kernel)
#                 is_motion = mean_of_mask > threshold
#                 if is_motion:
#                     video_writer.write(src_frame)
#             pivot = frame_t
#             frame_t = frame
#     else:
#         pivot = frame_t
#         frame_t = frame
#
# video_reader.release()
# video_writer.release()
