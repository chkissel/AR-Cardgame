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

        # H = self.smoothOverFrames(H)

        return H

    def smoothOverFrames(self, H):
        #Smooth the result over multiple frames
        self.last_Hs.append(H)
        if len(self.last_Hs) > self.max_Hs:
            self.last_Hs.pop(0)

        for h in self.last_Hs:
            H = H + h

        H = H / len(self.last_Hs)

        return H

    def drawRect(self, img, card_img, width, color, homography):
        # Build edge points out of card image
        h, w = card_img.shape
        p1 = [0, 0]
        p2 = [0, h - 1]
        p3 = [w - 1, h - 1]
        p4 = [w - 1, 0]
        points = np.float32([[p1], [p2], [p3], [p4]])

        # Transform points and build frame out of transformed points
        tpoints = cv2.perspectiveTransform(points, homography)

        drawn = cv2.polylines(img, [np.int32(tpoints)], True, color, width, cv2.LINE_AA)

        return drawn

    def checkRotation(self, homography):
        p1_color = (211, 27, 27)
        p2_color = (27, 27, 211)
        active = False

        # Check if card belongs to left or right player
        if homography[0,1] < 0:
            color = p1_color
        else:
            color = p2_color

        # Check if card is active or inactive
        h_degree = np.degrees(math.atan2(homography[0,1] , homography[1,1]))
        if (h_degree > 45 and h_degree < 135) or (h_degree < -45 and h_degree > -135):
            active = True

        width = 3 if active else 1

        return width, color

    def writeInformation(self, img, status):
        text = 'Player 1: ' + str(status[0]) + ' cards, ' + str(status[1]) + ' active | ' + 'Player 2: ' + str(status[2]) + ' cards, ' + str(status[3]) + ' active'
        drawn = cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 125, 0))
        return drawn

    def calcProjection(self, homography):
        # Clear homography from camera distortion
        homography = homography * (-1)
        cleared_matrix = np.dot(np.linalg.inv(self.camera_params), homography)
        col_1 = cleared_matrix[:, 0] # rot1
        col_2 = cleared_matrix[:, 1] # rot2
        col_3 = cleared_matrix[:, 2] # trans

        # Normalize vectors
        l = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))
        rot_1 = col_1 / l
        rot_2 = col_2 / l
        translation = col_3 / l

        # Turns the model to the left / right based on card direction
        # while giving the expected result, an offset to the center occurs
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

        # rotate before translation
        projection = np.array([rot_1, rot_2, rot_3]).T

        # Turns the card around the given degree
        # however the model now has a noticable offset to the center
        # theta = np.radians(90)
        # row_1 = [np.cos(theta), -np.sin(theta), 0]
        # row_2 = [np.sin(theta), np.cos(theta), 0]
        # row_3 = [0, 0, 1]
        # rot_z = np.matrix([row_1, row_2, row_3])
        # projection = projection * rot_z

        projection = np.c_[ projection, translation]

        return np.dot(self.camera_params, projection), translation

    # Used here for development purposes only
    # credits: https://www.learnopencv.com/rotation-matrix-to-euler-angles/
    # Checks if a matrix is a valid rotation matrix
    def isRotationMatrix(self, R) :
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        I = np.identity(3, dtype = R.dtype)
        n = np.linalg.norm(I - shouldBeIdentity)
        return n < 1e-6

    # credits: https://www.learnopencv.com/rotation-matrix-to-euler-angles/
    # Calculates rotation matrix to euler angles
    def rotationMatrixToEulerAngles(self, R) :

        assert(self.isRotationMatrix(R))

        sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])

        singular = sy < 1e-6

        if  not singular :
            x = math.atan2(R[2,1] , R[2,2])
            y = math.atan2(-R[2,0], sy)
            z = math.atan2(R[1,0], R[0,0])
        else :
            x = math.atan2(-R[1,2], R[1,1])
            y = math.atan2(-R[2,0], sy)
            z = 0

        return np.array([np.degrees(x), np.degrees(y), np.degrees(z)])
