import cv2


class VideoCapturer:
    def __init__(self, *args, **kwargs):
        self.__cap = cv2.VideoCapture(*args, **kwargs)
    @property
    def fps(self):
        return int(self.__cap.get(cv2.CAP_PROP_FPS))

    @property
    def width(self):
        return int(self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def length(self):
        return int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def isOpened(self):
        return self.__cap.isOpened()

    def read(self, image=None):
        return self.__cap.read(image)

    def grab(self):
        return self.__cap.grab()

    def retrieve(self, image=None, flag=None):
        return self.__cap.retrieve(image, flag)

    def release(self):
        return self.__cap.release()

