import cv2
import numpy as np


class CompareImage(object):

    def __init__(self, image_1_path, image_2_path):
        self.minimum_commutative_image_diff = 0.001
        self.image_1_path = image_1_path
        self.image_2_path = image_2_path

    def compare_image(self):
        image_1 = cv2.imread(self.image_1_path, 0)
        image_2 = cv2.imread(self.image_2_path, 0)
        commutative_image_diff = self.get_image_difference(image_1, image_2)

        if commutative_image_diff < self.minimum_commutative_image_diff:
            print("Matched")
            return {"Matched": True, "diff": commutative_image_diff}
        print("UnMatched")
        return {"Matched": False, "diff": commutative_image_diff}  # random failure value

    @staticmethod
    def get_image_difference(image_1, image_2):
        first_image_hist = cv2.calcHist([image_1], [0], None, [512], [0, 512])
        second_image_hist = cv2.calcHist([image_2], [0], None, [512], [0, 512])

        img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_BHATTACHARYYA)
        img_template_probability_match = \
            cv2.matchTemplate(first_image_hist, second_image_hist, cv2.TM_CCOEFF_NORMED)[0][0]
        img_template_diff = 1 - img_template_probability_match

        # taking only 10% of histogram diff, since it's less accurate than template method
        commutative_image_diff = (img_hist_diff / 10) + img_template_diff
        return commutative_image_diff

    def is_similar_gray(self):
        # colored Image  1, Black and White (gray scale)  0
        image1 = cv2.imread(self.image_1_path, 0)
        image2 = cv2.imread(self.image_2_path, 0)
        return image1.shape == image2.shape and not (np.bitwise_xor(image1, image2).any())

    def is_similar_colored(self):
        # colored Image  1, Black and White (gray scale)  0
        image1 = cv2.imread(self.image_1_path, 1)
        image2 = cv2.imread(self.image_2_path, 1)
        return image1.shape == image2.shape and not (np.bitwise_xor(image1, image2).any())


if __name__ == '__main__':
    '''
    compare_image = CompareImage('/Users/anna/xxx4-selenium/screen/plaza_layer/no_dp.png',
                                 '/Users/anna/xxx4-selenium/screen/plaza_layer/no_mall.png')
    image_difference = compare_image.compare_image()
    print(image_difference)

    compare_image1 = CompareImage('/Users/anna/xxx4-selenium/screen/plaza_layer/no_dp.png',
                                  '/Users/anna/xxx4-selenium/screen/plaza_layer/no_mall.png')
    print(compare_image.is_similar_colored())
    '''
