import cv2
import numpy as np
import yaml


class PrettySafeLoader(yaml.SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))

PrettySafeLoader.add_constructor(
    u'tag:yaml.org,2002:python/tuple',
    PrettySafeLoader.construct_python_tuple)

def read_tuple_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(yaml.load_all(f, Loader=PrettySafeLoader))

def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(yaml.safe_load_all(f))

def is_similar_gray(image1, image2):
    # colored Image  1, Black and White (gray scale)  0
    image1 = cv2.imread(image1, 0)
    image2 = cv2.imread(image2, 0)
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())


def is_similar_colored(image1, image2):
    # colored Image  1, Black and White (gray scale)  0
    image1 = cv2.imread(image1, 1)
    image2 = cv2.imread(image2, 1)
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())

def compare_img_with_difference(image1, image2):
    image1 = cv2.imread(image1, 1)
    image2 = cv2.imread(image2, 1)
    minimum_commutative_image_diff = 0.001
    first_image_hist = cv2.calcHist([image1], [0], None, [512], [0, 512])
    second_image_hist = cv2.calcHist([image2], [0], None, [512], [0, 512])

    img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_BHATTACHARYYA)
    img_template_probability_match = \
        cv2.matchTemplate(first_image_hist, second_image_hist, cv2.TM_CCOEFF_NORMED)[0][0]
    img_template_diff = 1 - img_template_probability_match
    # taking only 10% of histogram diff, since it's less accurate than template method
    commutative_image_diff = (img_hist_diff / 10) + img_template_diff
    if commutative_image_diff < minimum_commutative_image_diff:
        print("Matched")
        return {"Matched": True, "diff": commutative_image_diff}
    print("UnMatched")
    return {"Matched": False, "diff": commutative_image_diff}  # random failure value




if __name__ == '__main__':
    print(read_tuple_yaml('../data/plaza1.yaml'))
