import cv2
from renderingClass import OBJ


class Card:

    def __init__(self, name, scale, featureInstance):
        self.name = name

        img = cv2.imread('assets/' + name + '.png')
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        obj = OBJ(('assets/' + name + '.obj'), swapyz=True)
        self.obj = obj
        self.scale = scale

        self.kp, self.des = featureInstance.extract(self.img)

        print('Card ' + name + ' read and processed')
