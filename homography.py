import cv2
import numpy as np


class Homography:

    def __init__(self, img_kp, card_kp, matches):
        self.matches = matches
        self.img_kp = img_kp
        self.card_kp = card_kp

    def compute(self):
        # Collect the matching keypoints in both images
        src_pts = np.float32([self.img_kp[m.queryIdx].pt for m in self.matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.card_kp[m.trainIdx].pt for m in self.matches]).reshape(-1, 1, 2)

        # Compute Homography with ransac
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        return H

    def draw(self, img, card_img, matrix):
        # Build edge points out of card image
        h, w = card_img.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Transform points and build frame out of edges
        dst = cv2.perspectiveTransform(pts, matrix)
        drawn = cv2.polylines(img, [np.int32(dst)], True, 255, 2, cv2.LINE_AA)

        return drawn
