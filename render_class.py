
from panda3d.core import *
from panda3d.core import Texture
from direct.gui.OnscreenImage import OnscreenImage

from featureClass import FeatureClass
from geometryClass import GeometryClass
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor


import numpy as np


from card import Card

import sys

import cv2


class Game(ShowBase):

    def get_cv_img(self):
        """ This method uses PTAUchar and another bit of pointer trickery.
            The setup2dTexture must be for the right image properties.
        """
        success, img = self.cap.read()  # img is a numpy array
        print
        "success", success


        # Extract keypoints
        kp, des = self.features.extract(img)

        # Match extracted keypoints and card keypoints
        matches = self.features.match(des, self.card.des)
        # img = self.features.draw(matches, img, self.card.img, kp, self.card.kp)

        if len(matches) > self.features.MINMATCHES:
            # Calculate homography matrix
            H = self.geometry.computeHomography(kp, self.card.kp, matches)
            frame = self.geometry.drawRect(img, self.card.img, self.card.color, H)
            projection = self.geometry.calcProjection(H)
            self.translation = projection[:, 3]

            # NORMALIZE! 1 = max, TODO
            # self.norm_trans = (self.translation - np.min(self.translation)) / np.ptp(self.translation)
            # frame = render(frame, card.obj, card.scale, card.color, card.img, projection, False)
        """
        # Calculate homography matrix
        H = self.geometry.computeHomography(kp, self.card.kp, matches)
        # frame = geometry.draw(frame, card.img, H)
        projection = self.geometry.calcProjection(H)
        """
        if success:
            shape = img.shape  # (720, 1280, 3)

            self.img = cv2.flip(img, 0)  # cv2 image is upside down
            self.tex = Texture("detect")
            self.tex.setCompression(Texture.CMOff)  # 1 to 1 copying - default, so is unnecessary
            self.tex.setup2dTexture(shape[1], shape[0],
                                    Texture.TUnsignedByte, Texture.FRgb)  # FRgba8) # 3,4 channel

            p = PTAUchar.emptyArray(0)

            p.setData(self.img)
            self.tex.setRamImage(CPTAUchar(p))


    def __init__(self):
        ShowBase.__init__(self)


        # initialise cv2 camera
        self.cap = cv2.VideoCapture(0)  # first camera
        # self.cap = cv2.VideoCapture(1)  # second camera

        self.features = FeatureClass(min_matches=20, max_matches = 75)
        self.geometry = GeometryClass()

        self.card = Card('card_1', 50, (27, 27, 211), self.features)

        ch = cv2.waitKey(1) & 0xFF
        if ch == ord('1'):
            self.mode = 1

        for i in range(10):
            self.cap.read()

        #sm = CardMaker('bg')
        #self.test = self.render2d.attachNewNode(sm.generate(), 2)

        self.get_cv_img()

        # self.test.setTexture(self.tex)
        self.test = OnscreenImage(parent=self.render2d, image=self.tex, scale=(1.0), pos=(0, 0, 0))
        self.cam.node().getDisplayRegion(0).setSort(20)

        dlight = DirectionalLight('my dlight')
        dlnp = self.render.attachNewNode(dlight)

        #self.model = self.loader.loadModel("assets/card_1.obj")
        self.model = Actor("models/panda-model",
                           {"walk": "models/panda-walk4"})
        # Reparent the model to render.
        self.model.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.model.setScale(0.005, 0.005, 0.005)

        # x,y ca. bis 10!
        self.model.setPos(0, 25, 0)
        # letzte Spalte von projection == Position
        self.model.setLight(dlnp)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.turn, "turn")

    def turn(self, task):
        # continually call cap.read() here to update the texture
        self.get_cv_img()
        self.test.setTexture(self.tex)
        print
        "looping"
        # z is up! https://docs.panda3d.org/1.10/python/programming/scene-graph/common-state-changes
        # self.model.setPos(self.translation[0], self.translation[2], self.translation[1])
        self.model.setPos(0, 25, self.translation[1])
        print(self.model.getPos())
        # self.model.setPos(self.norm_trans[0], self.norm_trans[1], self.norm_trans[2])
        return task.cont

app = Game()
app.run()