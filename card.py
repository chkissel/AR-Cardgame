import cv2
from featureDesc import FeatureDescriptor


class Card:

    def __init__(self, name):
        self.name = name

        img = cv2.imread('assets/' + name + '.png')
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        features = FeatureDescriptor(self.img)
        self.kp, self.des = features.extract()

        print('Card ' + name + ' read and processed')
