#!/usr/bin/env python3
import cv2
import numpy as np
import time

from featureClass import FeatureClass
from geometryClass import GeometryClass
from renderingClass import RenderingClass

from card import Card


def game(fps, video):
    if (fps):
        start_time = time.time()
        interval = 1 # displays the frame rate every x second
        counter = 0

    # Initialize instances
    features = FeatureClass(min_matches = 20, max_matches = 75)
    geometry = GeometryClass()
    rendering = RenderingClass()

    card_1 = Card('card_1', 50, features)
    card_2 = Card('card_2', 25, features)
    card_3 = Card('card_6', 25, features)
    card_4 = Card('card_5', 50, features)

    # cards = [card_1, card_2, card_3, card_4]
    cards = [card_1, card_2, card_4]
    # cards = [card_1, card_2]
    # cards = [card_1]

    # [blueCards, blueActive, redCards, redActive]
    card_stati = [0, 0, 0, 0]

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
                    card_stati = collectInformation(card_stati, width, color)
                    frame = geometry.drawRect(frame, card.img, width, color, H)

                    # Seperate translation only used for Panda3D
                    projection, transl = geometry.calcProjection(H)
                    frame = rendering.render(frame, card.obj, card.scale, color, card.img, projection)

            frame = geometry.writeInformation(frame, card_stati)
            card_stati = [0, 0, 0, 0]

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

    # Stop the capture
    cap.release()
    if (video):
        out.release()
    cv2.destroyAllWindows()

def collectInformation(stati, width, color):
    p1_color = (211, 27, 27)
    active_width = 3

    if color == p1_color:
        stati[0] = stati[0] + 1
        if width == active_width:
            stati[1] = stati[1] + 1
    else:
        stati[2] = stati[2] + 1
        if width == active_width:
            stati[3] = stati[3] + 1

    return stati




if __name__ == "__main__":
    game(fps=True, video=False)
