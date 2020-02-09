from panda3d.core import *
from panda3d.core import Texture
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from card import Card
from featureClass import FeatureClass
from geometryClass import GeometryClass

import sys
import numpy as np
import math

import cv2


class Game(ShowBase):

    def game(self):
        success, img = self.cap.read()

        # Find keypoints
        kp, des = self.features.extract(img)

        # Match keypoints
        matches = self.features.match(des, self.card.des)

        # uncomment for drawing keypoints
        # img = self.features.draw(matches, img, self.card.img, kp, self.card.kp)

        if len(matches) > self.features.MINMATCHES:
            # Homography & projection matrix
            H = self.geometry.computeHomography(kp, self.card.kp, matches)
            self.offset, frame = self.geometry.drawRect(img, self.card.img, self.card.color, H)
            self.projection, self.translation = self.geometry.calcProjection(H)

        if success:
            # Create texture from openCV image
            # https://discourse.panda3d.org/t/opencv-image-as-a-panda-texture-clarification/12480/3
            shape = img.shape  # (720, 1280, 3)
            self.img = cv2.flip(img, 0)
            self.tex = Texture("detect")
            self.tex.setup2dTexture(shape[1], shape[0],
                                    Texture.TUnsignedByte, Texture.FRgb)
            p = PTAUchar.emptyArray(0)
            p.setData(self.img)
            self.tex.setRamImage(CPTAUchar(p))

    def __init__(self):
        ShowBase.__init__(self)
        # initialise cv2 camera
        self.cap = cv2.VideoCapture(0)
        # (1) for external webcam
        # self.cap = cv2.VideoCapture(1)

        # Initialise game classes
        self.features = FeatureClass(min_matches=20, max_matches = 75)
        self.geometry = GeometryClass()
        self.card = Card('card_1', 50, (27, 27, 211), self.features)

        ch = cv2.waitKey(1) & 0xFF
        if ch == ord('1'):
            self.mode = 1

        # Start image processing
        self.game()

        # Render webcam texture to background
        self.test = OnscreenImage(parent=self.render2d, image=self.tex, scale=1.0, pos=(0, 0, 0))
        self.cam.node().getDisplayRegion(0).setSort(20)

        # Set directional light
        dlight = DirectionalLight('my dlight')
        dlnp = self.render.attachNewNode(dlight)

        # Load model
        self.model = Actor("models/panda-model",
                           {"walk": "models/panda-walk4"})

        # Scale and flip model on Y
        self.model.setScale(0.03, -0.03, 0.03)
        self.model.setAttrib(CullFaceAttrib.makeReverse())
        self.model.setPos(0, 25, 0)

        # Reparent the model to render.
        self.model.reparentTo(self.render)

        # Animate model
        self.model.loop("walk")

        # Apply directional light to model
        self.model.setLight(dlnp)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.loop, "loop")

    def loop(self, task):
        self.game()
        self.test.setTexture(self.tex)

        # Apply rotation and displacement to the model
        x = -self.translation[0]/10# + self.offset[0]/10
        y = -self.translation[2]/10
        z = self.translation[1]/10# - self.offset[1]/10

        self.model.setPos(x, y, z)

        angles = self.rotationMatrixToEulerAngles(self.projection[:3])

        z = angles[2] + 180
        x = angles[1]
        y = -angles[0] + 90

        self.model.setHpr(x, y, z)

        return task.cont

    def rotationMatrixToEulerAngles(self, R):
        # Calculate euler angles from projection matrix
        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(R[2, 1], R[2, 2])
            y = math.atan2(-R[2, 0], sy)
            z = math.atan2(R[1, 0], R[0, 0])
        else:
            x = math.atan2(-R[1, 2], R[1, 1])
            y = math.atan2(-R[2, 0], sy)
            z = 0

        return np.array([np.degrees(x), np.degrees(y), np.degrees(z)])


app = Game()
app.run()
