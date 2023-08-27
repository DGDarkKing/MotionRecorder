import cv2


def translate_frame(frame, interesting_area):
    frame = frame[
            interesting_area[0][1]:interesting_area[1][1],
            interesting_area[0][0]:interesting_area[1][0]
            ]
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def diffImage(frame_t_minus, frame_t, frame_t_plus, kernel):
    delta_t_plus = cv2.absdiff(frame_t_plus, frame_t)
    delta_t = cv2.absdiff(frame_t, frame_t_minus)
    mask_frame = cv2.bitwise_and(delta_t_plus, delta_t)
    # _, mask_frame = cv2.threshold(mask_frame, 70, 200, cv2.THRESH_TOZERO)
    mask_frame = cv2.morphologyEx(mask_frame, cv2.MORPH_OPEN, kernel)
    return mask_frame, mask_frame.mean()

