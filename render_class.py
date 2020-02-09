
from panda3d.core import *
from panda3d.core import Texture
from direct.gui.OnscreenImage import OnscreenImage

from featureClass import FeatureClass
from geometryClass import GeometryClass
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import Mat4


import numpy as np
import math

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
            self.offset, frame = self.geometry.drawRect(img, self.card.img, self.card.color, H)
            self.projection, self.translation = self.geometry.calcProjection(H)
            proj = self.scale(self.projection, 0, 10)
            proj = np.append(proj, [[0, 0, 0, 1]], axis=0)

            """
            mat = Mat4(proj[0:1,0:1], proj[1:2,0:1], proj[2:3,0:1], proj[3:,0:1],
                       proj[0:1,2:3], proj[1:2,2:3], proj[2:3,2:3], proj[3:,2:3],
                       proj[0:1,1:2], proj[1:2,1:2], proj[2:3,1:2], proj[3:,1:2],
                       proj[0:1,:3], proj[1:2,:3], proj[2:3,:3], proj[3:,:3])





            self.mat = Mat4(proj.item(0,0), proj.item(0,1), proj.item(0,2), 0,
                       proj.item(2,0), proj.item(2,1), proj.item(2,2), 25,
                       proj.item(1,0), proj.item(1,1), proj.item(1,2), 0,
                       proj.item(3,0), proj.item(3,1), proj.item(3,2), 0)

"""
            self.mat = Mat4(proj.item(0, 0), proj.item(0, 1), proj.item(0, 2), proj.item(0, 3),
                            proj.item(1, 0), proj.item(1, 1), proj.item(1, 2), proj.item(1, 3),
                            proj.item(2, 0), proj.item(2, 1), proj.item(2, 2), proj.item(2, 3),
                            proj.item(3, 0), proj.item(3, 1), proj.item(3, 2), proj.item(3, 3))


            #self.norm_projection = self.scale(self.projection, self.projection.min(), self.projection.max())
            #self.translation = projection[:, 3]


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

        # self.model = self.loader.loadModel("assets/card_1.obj")
        # self.model.setScale(5.0, 5.0, 5.0)
        self.model = Actor("models/panda-model",
                           {"walk": "models/panda-walk4"})

        # Scale and flip model on Y
        self.model.setScale(0.03, -0.03, 0.03)
        self.model.setAttrib(CullFaceAttrib.makeReverse())
        # Reparent the model to render.
        self.model.reparentTo(self.render)
        self.model.loop("walk")
        # Apply scale and position transforms on the model.
        #self.model.setScale(0.025, 0.025, 0.025)

        # x,y ca. bis 10!
        self.model.setPos(0, 25, 0)
        # letzte Spalte von projection == Position
        self.model.setLight(dlnp)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.turn, "turn")

    def turn(self, task):
        self.get_cv_img()
        self.test.setTexture(self.tex)

        # z is up! https://docs.panda3d.org/1.10/python/programming/scene-graph/common-state-changes

        x = -self.translation[0]/10# + self.offset[0]/10
        y = -self.translation[2]/10
        z = self.translation[1]/10# - self.offset[1]/10
        #^ offset is still rigged

        self.model.setPos(x, y, z)

        angles = self.rotationMatrixToEulerAngles(self.projection[:3])

        # works as long as z == 0
        z = angles[2] + 180
        x = angles[1]
        y = -angles[0] + 90
        # print('z', abs(z * 0.01))
        # print(abs(z) * 0.01)
        # print(abs(z))
        # print(math.sin(abs(z)))
        # flip = abs(math.sin(abs(z) * 0.01))
        # print('flip', flip, (1-flip))
        # x = (1-flip) * x - flip * y
        # y = (1-flip) * y + flip * x


        # x = x * math.cos(z) - y * math.sin(z)
        # y = x * math.sin(z) + y * math.cos(z)

        self.model.setHpr(x, y, z)

        # if z is no longer 0 x and y are flipped
        # print(self.model.getHpr())

        return task.cont

    def scale(self, X, x_min, x_max):
        nom = (X - X.min(axis=0)) * (x_max - x_min)
        denom = X.max(axis=0) - X.min(axis=0)
        denom[denom == 0] = 1
        return x_min + nom / denom

    def rotationMatrixToEulerAngles(self, R) :

        # assert(self.isRotationMatrix(R))

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

app = Game()
app.run()
