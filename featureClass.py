import cv2


class FeatureClass:

    def __init__(self, min_matches=10, max_matches=20):
        self.MINMATCHES = min_matches
        self.MAXMATCHES = max_matches

        # Initiate BruteForce Matcher
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Initiate ORB detector
        self.orb = cv2.ORB_create()

    def extract(self, img):
        # find the keypoints with ORB
        kp = self.orb.detect(img, None)

        # compute the descriptors with ORB
        kp, des = self.orb.compute(img, kp)

        return kp, des

    def match(self, img_des, card_des):
        # Match frame descriptors with card descriptors
        matches = self.bf.match(img_des, card_des)

        # Sort them in the order of their distance
        matches = sorted(matches, key=lambda x: x.distance)

        # Limit amount of found matches, should be around 50
        matches = matches[:self.MAXMATCHES]

        return matches

    def draw(self, matches, img, card_img, img_kp, card_kp):
        # Draws matches between image and reference image
        matched = cv2.drawMatches(img, img_kp, card_img, card_kp,
                              matches[:self.MAXMATCHES], 0, flags=2)

        return matched
