import cv2


class FeatureClass:

    def __init__(self, min_matches=10, max_matches=50):
        self.MINMATCHES = min_matches
        self.MAXMATCHES = max_matches
        self.MAXDISTANCE = 50

        # Initiate matcher
        # self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.bf = cv2.BFMatcher()
        # self.flann = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)

        # Initiate detector
        # self.orb = cv2.ORB_create()
        self.sift = cv2.xfeatures2d.SIFT_create()
        # self.sift = cv2.xfeatures2d.SIFT_create(nfeatures=200)
        # self.surf = cv2.xfeatures2d.SURF_create(400)

    def extract(self, img):
        # kp, des = self.orb.detectAndCompute(img, None)
        kp, des = self.sift.detectAndCompute(img, None)
        # kp, des = self.surf.detectAndCompute(img, None)

        return kp, des

    def match(self, img_des, card_des):
        # Match frame descriptors with card descriptors
        # matches = self.bf.match(img_des, card_des)
        # matches = self.flann.match(img_des, card_des)
        #
        # # Sort them in the order of their distance
        # matches = sorted(matches, key=lambda x: x.distance)
        #
        # # Limit amount of found matches, should be around 50
        # matches = matches[:self.MAXMATCHES]
        #
        # # Apply ratio test
        # good = []
        # for m in matches:
        #     if m.distance < self.MAXDISTANCE:
        #         good.append(m)
        # return good

        matches = self.bf.knnMatch(img_des, card_des, k=2)
        # matches = self.flann.knnMatch(img_des, card_des, k=2)
        good = []
        for m,n in matches:
            if m.distance < 0.65*n.distance: # 0.8 for ORB
                good.append(m)

        return good

    def draw(self, matches, img, card_img, img_kp, card_kp):
        # Draws matches between image and reference image
        matched = cv2.drawMatches(img, img_kp, card_img, card_kp,
                              matches[:self.MAXMATCHES], 0, flags=2)

        return matched
