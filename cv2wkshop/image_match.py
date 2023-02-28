import numpy as np
import cv2
import imutils
from matplotlib import pyplot as plt


def color_match_diff_scale(source, template, visual):
    '''
    from 我老公 Adrian Rosebrock, Multi-scale Template Matching using Python and OpenCV
    https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
    稍微改了下，模板匹配时，用的是 TM_CCOEFF_NORMED 算法用以匹配彩色图片
    :param source: 大图
    :param template: 要找的小图
    :param visual: 运行中是否要渲染出图
    :return: 小图在大图的xy坐标
    '''
    source = cv2.imread(source)
    template = cv2.imread(template)
    (tH, tW) = template.shape[:2]
    found = None
    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        print('scale: ', scale)
        resized = imutils.resize(source, width=int(source.shape[1] * scale))
        r = source.shape[1] / float(resized.shape[1])

        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)  # match on colored image
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        # visual = False

        # check to see if the iteration should be visualized
        if visual:
            # draw a bounding box around the detected region
            # clone = np.dstack([template, template, template])
            cv2.rectangle(resized, (maxLoc[0], maxLoc[1]),
                          (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Visualize", resized)
            cv2.waitKey(0)
        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(source, (startX, startY), (endX, endY), (0, 0, 255), 2)
    if visual:
        cv2.imshow("Image", source)
        cv2.waitKey(0)
    return (startX + (endX - startX) / 2, startY + (endY - startY) / 2)
    raise Exception("Image not found")


def grey_match_diff_scale(img, template, visual):
    '''
    from 我老公 Adrian Rosebrock, Multi-scale Template Matching using Python and OpenCV
    https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
    稍微改了下，去掉命令行参数
    :param source: 大图
    :param template: 要找的小图
    :param visual: 运行中是否要渲染出图
    :return: 小图在大图的xy坐标
    '''
    # load the image, convert it to grayscale, and initialize the
    # bookkeeping variable to keep track of the matched region
    source = cv2.imread(img)
    template = cv2.imread(template)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 50, 200)
    (tH, tW) = template.shape[:2]

    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    found = None
    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        # print('scale: ', scale)
        resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
        r = gray.shape[1] / float(resized.shape[1])
        # print(r)
        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        # detect edges in the resized, grayscale image and apply template
        # matching to find the template in the image
        edged = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        # check to see if the iteration should be visualized
        if visual:
            # draw a bounding box around the detected region
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                          (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)
        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    # draw a bounding box around the detected result and display the image
    cv2.rectangle(source, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.imshow("Image", source)
    cv2.waitKey(0)
    return (startX + (endX - startX) / 2, startY + (endY - startY) / 2)
    raise Exception("Image not found")

def exact_match_img(img, tpl):
    '''
    在大图里找小图，小图必须是从原图里抠出来的，是精准查找，找到则返回x,y坐标，找不到则报错
    出处：https://stackoverflow.com/questions/29663764/determine-if-an-image-exists-within-a-larger-image-and-if-so-find-it-using-py
    回复者真是大师啊，膜拜
    稍微修改了下返回，让返回xy而不是yx。 还添加了直接用cv2打开图片的代码cv2.namedWindow, imshow等
    还有个参考：
    1. What could cause a Value Error in this short image matching function in Python (using numpy)?
       https://stackoverflow.com/questions/30797657/what-could-cause-a-value-error-in-this-short-image-matching-function-in-python?noredirect=1&lq=1
    2. Recognize recurring images into a larger one
       https://stackoverflow.com/questions/34310914/recognize-recurring-images-into-a-larger-one?noredirect=1&lq=1
    :param im: 大图
    :param tpl: 小图，要找的图
    :return:
    '''
    # print(img, tpl)
    im = cv2.imread(img, 1)
    size = im.shape
    print('img: ', size)
    tpl = cv2.imread(tpl, 1)

    '''
    如果已经发生了以某点为中心的跳转，那么可以直接取屏幕中心
    #tpl = im[170:220, 75:130].copy()
    y_from = int(size[1]/2-10)
    y_to = int(size[1] / 2 + 10)
    x_from = int(size[0] / 2 - 10)
    x_to = int(size[0] / 2 + 10)
    #print(x_from, x_to)
    tpl = im[x_from:x_to,y_from:y_to].copy()
    '''
    tpl_size = tpl.shape  # used to calculate offset
    print('tpl: ', tpl_size)

    im = np.atleast_3d(im)
    tpl = np.atleast_3d(tpl)
    H, W, D = im.shape[:3]
    h, w = tpl.shape[:2]

    # Integral image and template sum per channel
    sat = im.cumsum(1).cumsum(0)
    tplsum = np.array([tpl[:, :, i].sum() for i in range(D)])

    # Calculate lookup table for all the possible windows
    iA, iB, iC, iD = sat[:-h, :-w], sat[:-h, w:], sat[h:, :-w], sat[h:, w:]
    lookup = iD - iB - iC + iA
    # Possible matches
    possible_match = np.where(np.logical_and.reduce([lookup[..., i] == tplsum[i] for i in range(D)]))

    # Find exact match
    for y, x in zip(*possible_match):
        if np.all(im[y + 1:y + h + 1, x + 1:x + w + 1] == tpl):
            return (x + tpl_size[1] / 2, y + tpl_size[0] / 2)

    raise Exception("Image not found")


def template_matcher_img(big, small):
    '''
    模板匹配Template Matching----单目标匹配
    :return:
    '''
    # 读取目标图片
    target = cv2.imread(big)
    # 读取模板图片
    template = cv2.imread(small)
    # 获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # 归一化处理
    cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 匹配值转换为字符串
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    # 对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    # 显示结果,并将匹配值显示在标题栏上
    cv2.namedWindow('showimage')
    cv2.imshow("MatchResult----MatchingValue=" + strmin_val, target)
    # cv2.imshow("MatchResult----MatchingValue=" + strmin_val, template)
    cv2.waitKey()
    cv2.destroyAllWindows()


def template_matcher_multi_img(big, small):
    target = cv2.imread(big)
    # 读取模板图片
    template = cv2.imread(small)
    # 获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # 归一化处理
    # cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    # 匹配值转换为字符串
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    # 对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    # 初始化位置参数
    temp_loc = min_loc
    other_loc = min_loc
    numOfloc = 1
    # 第一次筛选----规定匹配阈值，将满足阈值的从result中提取出来
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法设置匹配阈值为0.01
    threshold = 0.01
    loc = np.where(result < threshold)
    # 遍历提取出来的位置
    for other_loc in zip(*loc[::-1]):
        # 第二次筛选----将位置偏移小于5个像素的结果舍去
        if (temp_loc[0] + 5 < other_loc[0]) or (temp_loc[1] + 5 < other_loc[1]):
            numOfloc = numOfloc + 1
            temp_loc = other_loc
            cv2.rectangle(target, other_loc, (other_loc[0] + twidth, other_loc[1] + theight), (0, 0, 225), 2)
    str_numOfloc = str(numOfloc)
    # 显示结果,并将匹配值显示在标题栏上
    strText = "MatchResult----MatchingValue=" + strmin_val + "----NumberOfPosition=" + str_numOfloc
    cv2.imshow(strText, target)
    cv2.waitKey()
    cv2.destroyAllWindows()

def flann_matcher_points(big, small):
    '''
    基于FLANN的匹配器(FLANN based Matcher)描述特征点
    https://blog.csdn.net/zhuisui_woxin/article/details/84400439?utm_medium=distribute.pc_relevant.none-
    task-blog-BlogCommendFromMachineLearnPai2-2.channel_param&depth_1-utm_source=distribute.pc_relevant.
    none-task-blog-BlogCommendFromMachineLearnPai2-2.channel_param

    基于FLANN的匹配器(FLANN based Matcher)
    1.FLANN代表近似最近邻居的快速库。它代表一组经过优化的算法，用于大数据集中的快速最近邻搜索以及高维特征。
    2.对于大型数据集，它的工作速度比BFMatcher快。
    3.需要传递两个字典来指定要使用的算法及其相关参数等
    对于SIFT或SURF等算法，可以用以下方法：
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    对于ORB，可以使用以下参数：
    index_params= dict(algorithm = FLANN_INDEX_LSH,
               table_number = 6, # 12   这个参数是searchParam,指定了索引中的树应该递归遍历的次数。值越高精度越高
               key_size = 12,     # 20
               multi_probe_level = 1) #2
    :return:
    '''
    queryImage = cv2.imread(big, 0)
    trainingImage = cv2.imread(small, 0)  # 读取要匹配的灰度照片

    sift = cv2.xfeatures2d.SIFT_create()  # 创建sift检测器
    kp1, des1 = sift.detectAndCompute(queryImage, None)
    kp2, des2 = sift.detectAndCompute(trainingImage, None)
    # 设置Flannde参数
    FLANN_INDEX_KDTREE = 0
    indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    searchParams = dict(checks=50)
    flann = cv2.FlannBasedMatcher(indexParams, searchParams)
    matches = flann.knnMatch(des1, des2, k=2)
    # 设置好初始匹配值
    matchesMask = [[0, 0] for i in range(len(matches))]
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.5 * n.distance:  # 舍弃小于0.5的匹配结果
            matchesMask[i] = [1, 0]
    drawParams = dict(matchColor=(0, 0, 255), singlePointColor=(255, 0, 0), matchesMask=matchesMask,
                      flags=0)  # 给特征点和匹配的线定义颜色
    resultimage = cv2.drawMatchesKnn(queryImage, kp1, trainingImage, kp2, matches, None, **drawParams)  # 画出匹配的结果
    plt.imshow(resultimage, ), plt.show()

def flann_matcher_img(big, small):
    '''
    基于FLANN的匹配器(FLANN based Matcher)定位图片
    :return:
    '''
    MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量为10
    template = cv2.imread(big, 0)  # queryImage
    target = cv2.imread(small, 0)  # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv2.drawMatches(template, kp1, target, kp2, good, None, **draw_params)
    plt.imshow(result, 'gray')
    plt.show()


if __name__ == '__main__':
    template_matcher_multi_img('big.jpg', 'small2.jpg')
