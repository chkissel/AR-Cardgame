import cv2
import numpy as np
import math


class GeometryClass:

    def __init__(self):
        self.camera_params = np.array([[850, 0, 330], [0, 850, 230], [0, 0, 1]])
        # ^ Values are rounded from multiple chessboard calibrations

    def computeHomography(self, img_kp, card_kp, matches):
        # Collect the matching keypoints in both images
        src_pts = np.float32([img_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([card_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        # Compute Homography with ransac
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        return H

    def draw(self, img, card_img, homography):
        # Build edge points out of card image
        h, w = card_img.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Transform points and build frame out of edges
        dst = cv2.perspectiveTransform(pts, homography)
        drawn = cv2.polylines(img, [np.int32(dst)], True, 255, 1, cv2.LINE_AA)

        return drawn

    def calcProjection(self, homography):
        # Compute rotation along the x and y axis as well as the translation
        homography = homography * (-1)
        rot_and_transl = np.dot(np.linalg.inv(self.camera_params), homography)
        col_1 = rot_and_transl[:, 0]
        col_2 = rot_and_transl[:, 1]
        col_3 = rot_and_transl[:, 2]

        # normalise vectors
        l = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))
        rot_1 = col_1 / l
        rot_2 = col_2 / l
        translation = col_3 / l

        # compute the orthonormal basis
        c = rot_1 + rot_2
        p = np.cross(rot_1, rot_2)
        d = np.cross(c, p)
        rot_1 = np.dot(c / np.linalg.norm(c, 2) + d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_2 = np.dot(c / np.linalg.norm(c, 2) - d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_3 = np.cross(rot_1, rot_2)

        # finally, compute the 3D projection matrix from the model to the current frame
        projection = np.stack((rot_1, rot_2, rot_3, translation)).T
        return np.dot(self.camera_params, projection)
