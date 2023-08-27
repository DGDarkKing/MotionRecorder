import datetime
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from calculation import translate_frame, get_frame, diffImage

video_dir = 'D:\\Work\\Video samples\\GoldMining\\Front loader\\2023.08.21\\RawVideos'
video_name = 'test.mp4'
#                   left_top    bottom_right
interesting_area = [(600, 250), (1220, 520)]
cap_fps = 5
threshold = 0.5
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
video_reader = cv2.VideoCapture(video_name)
fourcc = cv2.VideoWriter_fourcc(*'mpv4')
video_writer = cv2.VideoWriter('test_result.mp4', fourcc, 10,
                               (interesting_area[1][0] - interesting_area[0][0],
                                 interesting_area[1][1] - interesting_area[0][1])
                               )
if not video_reader.isOpened():
    exit(1)
fps = int(video_reader.get(cv2.CAP_PROP_FPS))
length = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))


kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
required_frame_num = fps // cap_fps
_, pivot = video_reader.read()
pivot = translate_frame(pivot, interesting_area)
frame_number = 0
while frame_number <= required_frame_num:
    video_reader.grab()
    frame_number += 1
_, frame_t = video_reader.retrieve()
frame_t = translate_frame(frame_t, interesting_area)

while video_reader.grab():
    frame_number += 1
    if frame_number % required_frame_num != 0:
        continue
    frame = get_frame(video_reader, interesting_area)
    mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)
    cv2.putText(mask_frame, str(round(mean_of_mask, 4)), (50, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
    video_writer.write(mask_frame)

    # pivot = frame_t
    # frame_t = frame

    if is_motion := mean_of_mask > threshold:
        foreground = pivot
        pivot = frame_t
        frame_t = frame
        motion_frame = frame
        # cv2.putText(mask_frame, str(round(mean_of_mask, 4)), (50, 50),
        #             cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
        # video_writer.write(mask_frame)
        while is_motion and video_reader.grab():
            frame_number += 1
            if frame_number % required_frame_num != 0:
                continue
            frame = get_frame(video_reader, interesting_area)
            mask_frame, mean_of_mask = diffImage(pivot, frame_t, frame, kernel)
            is_motion = mean_of_mask > threshold
            if is_motion:
                motion_frame = frame
                cv2.putText(mask_frame, f'Motion: {str(round(mean_of_mask, 4))}', (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
                video_writer.write(mask_frame)
            else:
                mask_frame, mean_of_mask = diffImage(foreground, frame_t, frame, kernel)
                is_motion = mean_of_mask > threshold
                if is_motion:
                    motion_frame = frame
                    cv2.putText(mask_frame, f'Additional condition: {str(round(mean_of_mask, 4))}', (50, 50),
                                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
                    video_writer.write(mask_frame)
                else:
                    cv2.putText(mask_frame, str(round(mean_of_mask, 4)), (50, 50),
                                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
                    video_writer.write(mask_frame)

            pivot = frame_t
            frame_t = frame
        pass
    else:
        pivot = frame_t
        frame_t = frame

    # cv2.putText(mask_frame, str(round(mean_of_mask, 4)), (50, 50),
    #             cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))
    # if mean_of_mask > threshold:
    #     print(f'Frame num: {frame_number}')
    # video_writer.write(mask_frame)
    # pivot = frame

video_reader.release()
video_writer.release()
