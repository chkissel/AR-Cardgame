#!/usr/bin/env python3
import cv2
import numpy as np
import time

from featureClass import FeatureClass
from geometryClass import GeometryClass

from card import Card


def game(fps, video):
    if (fps):
        start_time = time.time()
        interval = 1 # displays the frame rate every x second
        counter = 0

    # Initialize instances
    features = FeatureClass(min_matches = 20, max_matches = 50)
    geometry = GeometryClass()

    card_1 = Card('card_1', 50, features)
    card_2 = Card('card_2', 25, features)
    card_3 = Card('card_6', 25, features)
    card_4 = Card('card_5', 50, features)
    # cards = [card_1, card_2, card_3, card_4]
    cards = [card_1, card_2]
    # cards = [card_1]

    cap = cv2.VideoCapture(0)
    if (video):
        out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))
    mode = 0
    while True:
        # Capture frame-by-frame
        ret_cam, frame = cap.read()

        # wait for key and switch to mode
        ch = cv2.waitKey(1) & 0xFF
        if ch == ord('1'):
            mode = 1
        elif ch == ord('q') or ch == 27:
            break

        if mode == 1:
            # Extract keypoints
            kp, des = features.extract(frame)

            for card in cards:
                # Match extracted keypoints and card keypoints
                matches = features.match(des, card.des)
                # frame = features.draw(matches, frame, card.img, kp, card.kp)

                if len(matches) > features.MINMATCHES:
                    # Calculate homography matrix
                    H = geometry.computeHomography(kp, card.kp, matches)
                    width, color = geometry.checkRotation(H)
                    frame = geometry.drawRect(frame, card.img, width, color, H)

                    projection = geometry.calcProjection(H)
                    frame = render(frame, card.obj, card.scale, color, card.img, projection, False)

        if (video):
            out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        if (fps):
            counter+=1
            if (time.time() - start_time) > interval :
                print("FPS: ", counter / (time.time() - start_time))
                counter = 0
                start_time = time.time()

    # When everything done, release the capture
    cap.release()
    if (video):
        out.release()
    cv2.destroyAllWindows()

def render(img, obj, scale, fill, card_img, projection, color=False):
    vertices = obj.vertices
    scale_matrix = np.eye(3) * scale
    h, w = card_img.shape

    for face in obj.faces:
        face_vertices = face[0]
        points = np.array([vertices[vertex - 1] for vertex in face_vertices])
        points = np.dot(points, scale_matrix)
        # render model in the middle of the reference surface. To do so,
        # model points must be displaced
        points = np.array([[p[0] + w / 2, p[1] + h / 2, p[2]] for p in points])
        dst = cv2.perspectiveTransform(points.reshape(-1, 1, 3), projection)
        imgpts = np.int32(dst)
        if color is False:
            cv2.fillConvexPoly(img, imgpts, fill)
        else:
            color = hex_to_rgb(face[-1])
            color = color[::-1] # reverse
            cv2.fillConvexPoly(img, imgpts, color)

    return img

if __name__ == "__main__":
    game(fps=True, video=False)
