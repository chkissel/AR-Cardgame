
from panda3d.core import *
from panda3d.core import Texture
from direct.gui.OnscreenImage import OnscreenImage

from featureClass import FeatureClass
from geometryClass import GeometryClass
from direct.showbase.ShowBase import ShowBase



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

        # Calculate homography matrix
        H = self.geometry.computeHomography(kp, self.card.kp, matches)
        # frame = geometry.draw(frame, card.img, H)
        projection = self.geometry.calcProjection(H)

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

        self.features = FeatureClass(max_matches=20)
        self.geometry = GeometryClass()

        self.card = Card('card_1', self.features)

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

        self.model = self.loader.loadModel("assets/card_1.obj")
        # Reparent the model to render.
        self.model.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.model.setScale(1, 1, 1)
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
        return task.cont

app = Game()
app.run()