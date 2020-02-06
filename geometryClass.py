import cv2
import numpy as np
import math


class GeometryClass:

    def __init__(self):
        self.camera_params = np.array([[850, 0, 330], [0, 850, 230], [0, 0, 1]])
        # ^ Values are rounded from multiple chessboard calibrations
        self.last_Hs = []
        self.max_Hs = 5

    def computeHomography(self, img_kp, card_kp, matches):
        # Collect the matching keypoints in both images
        src_pts = np.float32([img_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([card_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)


        # Compute Homography with ransac
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        # Smooth the result over multiple frames
        # self.last_Hs.append(H)
        # if len(self.last_Hs) > self.max_Hs:
        #     self.last_Hs.pop(0)
        #
        # for h in self.last_Hs:
        #     H = H + h
        #
        # H = H / len(self.last_Hs)

        return H

    def drawRect(self, img, card_img, card_color, homography):
        # Build edge points out of card image
        h, w = card_img.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Transform points and build frame out of edges
        dst = cv2.perspectiveTransform(pts, homography)
        drawn = cv2.polylines(img, [np.int32(dst)], True, card_color, 1, cv2.LINE_AA)

        return drawn

    def calcProjection(self, homography):
        # Compute rotation along the x and y axis as well as the translation
        homography = homography * (-1)
        rot_and_transl = np.dot(np.linalg.inv(self.camera_params), homography)
        col_1 = rot_and_transl[:, 0] # rot1
        col_2 = rot_and_transl[:, 1] # rot2
        col_3 = rot_and_transl[:, 2] # trans

        # Normalize vectors
        l = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))
        rot_1 = col_1 / l
        rot_2 = col_2 / l
        translation = col_3 / l

        # This mess turns the model to the left / right based on card direction
        # theta = np.radians(90)
        # row_1 = [np.cos(theta), -np.sin(theta), 0]
        # row_2 = [np.sin(theta), np.cos(theta), 0]
        # row_3 = [0, 0, 1]
        # rot_mat = np.array([row_1, row_2, row_3])
        #
        # rotations = np.array([rot_1, rot_2, [0, 0, 1]]).T
        # rotations = rot_mat * rotations
        #
        # rot_1 = rotations[:, 0]
        # rot_2 = rotations[:, 1]

        # compute the orthonormal basis
        c = rot_1 + rot_2
        p = np.cross(rot_1, rot_2)
        d = np.cross(c, p)
        rot_1 = np.dot(c / np.linalg.norm(c, 2) + d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_2 = np.dot(c / np.linalg.norm(c, 2) - d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_3 = np.cross(rot_1, rot_2)

        # projection = np.stack((rot_1, rot_2, rot_3, translation)).T
        # print('pre', projection)

        # rotate before adding translation
        projection = np.array([rot_1, rot_2, rot_3]).T

        # This mess turns the card around the given degree
        # however the model now has a noticable offset to the center
        # theta = np.radians(90)
        ## row_1 = [np.cos(theta), -np.sin(theta), -translation[0]*np.cos(theta)+translation[1]*np.sin(theta)+translation[0]]
        ## row_2 = [np.sin(theta), np.cos(theta), -translation[0]*np.sin(theta)-translation[1]*np.cos(theta)+translation[1]]
        # row_1 = [np.cos(theta), -np.sin(theta), 0]
        # row_2 = [np.sin(theta), np.cos(theta), 0]
        # row_3 = [0, 0, 1]
        # rot_z = np.matrix([row_1, row_2, row_3])
        # print(rot_z)
        # projection = rot_z * projection
        # translation = np.dot(translation, rot_z)

        # Add translation as last column
        projection = np.c_[ projection, translation]

        return np.dot(self.camera_params, projection)
