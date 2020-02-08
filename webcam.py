# Copyright (C) 2015 Ross D Milligan
# GNU GENERAL PUBLIC LICENSE Version 3 (full notice can be found at https://github.com/rdmilligan/SaltwashAR)

import cv2
from threading import Thread


class Webcam:

    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        #self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
        #self.video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
        self.current_frame = self.video_capture.read()[1]

    # create thread for capturing images
    def start(self):
        Thread(target=self._update_frame, args=()).start()

    def _update_frame(self):
        while (True):
            self.current_frame = self.video_capture.read()[1]

    # get the current frame
    def get_current_frame(self):
        return self.current_frame
