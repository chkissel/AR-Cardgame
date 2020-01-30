import cv2


class FeatureMatcher:

    def __init__(self, img_kp, img_des, card_kp, card_des):
        self.img_kp = img_kp
        self.img_des = img_des
        self.card_kp = card_kp
        self.card_des = card_des
        self.MATCHES = 30

    def match(self):
        # Initiate BruteForce Matcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match frame descriptors with card descriptors
        matches = bf.match(self.img_des, self.card_des)

        # Sort them in the order of their distance
        matches = sorted(matches, key=lambda x: x.distance)

        return matches

    def draw(self, matches, img, card_img):
        # Draws matches between image and reference image
        matched = cv2.drawMatches(img, self.img_kp, card_img, self.card_kp,
                              matches[:self.MATCHES], 0, flags=2)

        return matched
