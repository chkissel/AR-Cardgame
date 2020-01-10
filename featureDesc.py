import cv2


class FeatureDescriptor:

    def __init__(self, img):
        self.img = img

    def extract(self):
        # Initiate ORB detector
        orb = cv2.ORB_create()

        # find the keypoints with ORB
        kp = orb.detect(self.img, None)

        # compute the descriptors with ORB
        kp, des = orb.compute(self.img, kp)

        # draw only keypoints location,not size and orientation
        # img2 = cv2.drawKeypoints(img, kp, img, color=(0, 255, 0), flags=0)

        return kp, des
