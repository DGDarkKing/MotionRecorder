import os.path

# conda install -c conda-forge opencv
import cv2

from calculation import translate_frame, diffImage

video_dir = 'VideoDirectory'
video_name = 'InputName'
#
output_name = 'OutputName'
#                   left_top    bottom_right
interesting_area = [(600, 250), (1220, 520)]
cap_fps = 5
threshold = 0.5
codec = 'avc1'
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
video_path = os.path.join(video_dir, video_name)
try:
    video_reader = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    fps = int(video_reader.get(cv2.CAP_PROP_FPS))
    width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_writer = cv2.VideoWriter(output_name, fourcc, fps, (width, height))
except Exception as e:
    pass
if not video_reader.isOpened():
    print("FAILED TO OPEN VIDEO")
    exit(1)
length = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
required_frame_num = fps // cap_fps
_, src_pivot = video_reader.read()
pivot = translate_frame(src_pivot, interesting_area)
frame_number = 0
while frame_number <= required_frame_num:
    video_reader.grab()
    frame_number += 1
_, src_frame_t = video_reader.retrieve()
frame_t = translate_frame(src_frame_t, interesting_area)

while video_reader.grab():
    frame_number += 1
    if frame_number % required_frame_num != 0:
        continue
    _, src_frame = video_reader.retrieve()
    frame = translate_frame(src_frame, interesting_area)
    mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)

    if is_motion := mean_of_mask > threshold:
        foreground = pivot
        pivot = frame_t
        frame_t = frame
        video_writer.write(src_frame)
        while is_motion and video_reader.grab():
            frame_number += 1
            _, src_frame = video_reader.retrieve()
            if frame_number % required_frame_num != 0:
                video_writer.write(src_frame)
                continue
            frame = translate_frame(src_frame, interesting_area)
            mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)
            is_motion = mean_of_mask > threshold
            if is_motion:
                video_writer.write(src_frame)
            else:
                mask_frame, mean_of_mask = diffImage(foreground, frame_t, frame, kernel)
                is_motion = mean_of_mask > threshold
                if is_motion:
                    video_writer.write(src_frame)
            pivot = frame_t
            frame_t = frame
    else:
        pivot = frame_t
        frame_t = frame

video_reader.release()
video_writer.release()
