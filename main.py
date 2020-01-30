#!/usr/bin/env python3
import cv2

from featureDesc import FeatureDescriptor
from featureMatch import FeatureMatcher
from homography import Homography

from card import Card


def game():
    card = Card('card_1')

    cap = cv2.VideoCapture(0)
    mode = 0
    while True:
        # Capture frame-by-frame
        ret_cam, frame = cap.read()

        # Initialize instances
        features = FeatureDescriptor(frame)

        # wait for key and switch to mode
        ch = cv2.waitKey(1) & 0xFF
        if ch == ord('1'):
            mode = 1
        elif ch == ord('q') or ch == 27:
            break

        if mode == 1:
            # Extract keypoints
            kp, des = features.extract()

            # Match extracted keypoints and card keypoints
            matcher = FeatureMatcher(kp, des, card.kp, card.des)
            matches = matcher.match()
            # frame = matcher.draw(matches, frame, card.img)

            # Calculate homography matrix
            homography = Homography(kp, card.kp, matches)
            H = homography.compute()
            frame = homography.draw(frame, card.img, H)

        # Display the resulting frame
        cv2.imshow('frame', frame)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    game()