import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys

from featureClass import FeatureClass
from geometryClass import GeometryClass
from card import Card

camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode([1280, 720])

try:
    while True:

        ret, frame = camera.read()

        # Initialize instances
        features = FeatureClass(min_matches=20, max_matches=75)
        geometry = GeometryClass()

        card = Card('card_1', 50, (27, 27, 211), features)

        kp, des = features.extract(frame)
        matches = features.match(des, card.des)

        if len(matches) > features.MINMATCHES:
            # Calculate homography matrix
            H = geometry.computeHomography(kp, card.kp, matches)
            frame = geometry.drawRect(frame, card.img, card.color, H)
            projection = geometry.calcProjection(H)


        screen.fill([0, 0, 0])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                sys.exit(0)

except KeyboardInterrupt as SystemExit:
    pygame.quit()
    cv2.destroyAllWindows()