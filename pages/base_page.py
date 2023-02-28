import logging
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from util.log import Logger
from util.config import Config
from util.find_xy_by_image import color_match_diff_scale
import os
import time
import numpy as np

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()
curr_time = time.strftime("%Y%m%d%H%M%S")
HOST = config.get_config('DEV', 'HOST') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'HOST')


class BasePage(object):
    def __init__(self, driver):
        super(BasePage, self).__init__()
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.language_locator = (By.CSS_SELECTOR, "a[title='Language'],a[title='语言']")
        self.map_canvas_locator = (By.TAG_NAME, "canvas") # width="1873" height="506"
        self.scale_locator = (By.CSS_SELECTOR, "div[class='ol-scale-line ol-unselectable']>div[class='ol-scale-line-inner']")
        self.zoom_in_locator = (By.CSS_SELECTOR, "div[class='ol-zoom ol-unselectable ol-control']>button[class='ol-zoom-in']")
        self.zoom_out_locator = (By.CSS_SELECTOR, "div[class='ol-zoom ol-unselectable ol-control']>button[class='ol-zoom-out']")

    def get_map_canvas(self):
        return self.find_element(*self.map_canvas_locator)

    def get_user_map_sources(self):
        '''
        获取当前用户拥有的图层类型(除了note, 因为这个是所有人都有权限的)
        :return:
        layer_group_global_buildings
        '''
        # element>element	div > p	Selects all <p> elements where the parent is a <div> element
        all_layers= self.find_elements(By.CSS_SELECTOR, "#drag_list > li ")
        map_sources = list()
        for layer in all_layers:
            source = layer.get_attribute("class").replace('ng-scope layer_group_','').replace(' lg-multiple','')
            map_sources.append(source)
        return map_sources

    def get_current_languge(self):
        return 'ENG' if self.find_element(*self.language_locator).get_attribute("title") == 'Language' else 'CHN'

    def change_languge(self):
        self.find_element(*self.language_locator).click()
        time.sleep(1)
        if self.get_current_languge() == 'ENG':
            self.find_element(By.PARTIAL_LINK_TEXT, "简体中文").click()
        else:
            self.find_element(By.PARTIAL_LINK_TEXT, "English").click()

    def click_map_canvas_by_xy(self, x, y):
        '''
        点击地图上的某个点
        :param x:
        :param y:
        :return:
        '''
        print('clicked x: ', x, "y: ", y)
        print('rect: ', self.find_element(*self.map_canvas_locator).rect)
        ActionChains(self.driver).move_to_element_with_offset(self.find_element(*self.map_canvas_locator), x, y).pause(
            1).click().perform()

    def take_screenshot_element(self, element, filename):
        '''
        给元素截图, 提供子文件夹和文件名
        :param filename should end with png,jpg and so on
        :return:
        '''
        path_current_directory = os.path.dirname(os.path.dirname(__file__))
        image_name = config.get_config('SCREENSHOT', 'SCREENSHOT_PATH') + filename
        image_name = os.path.join(path_current_directory, image_name)
        element.screenshot(image_name)
        return image_name

    def image_loaded(self, imgElement):
        '''
        判断某个图片元素是否下载并加载成功
        :param imgElement:
        :return:
        '''
        js = "return arguments[0].complete && "+"typeof arguments[0].naturalWidth != \"undefined\" && "+"arguments[0].naturalWidth > 0"
        result = self.driver.execute_script(js, imgElement)
        if type(result) == bool:
            return result

    def find_element(self, *args):
        # return self.driver.find_element(*args)
        """
        这里用了显示等待WebDriverWait: 针对于某个特定的元素设置的等待时间，在设置时间内，
        默认每隔一段时间检测一次当前页面某个元素是否存在，如果在规定的时间内找到了元素，
        则直接执行，即找到元素就执行相关操作，如果超过设置时间检测不到则抛出异常。默认检测频率为0.5s。

        详细格式如下：
        WebDriverWait(driver, timeout, poll_frequency=0.5, ignored_exceptions=None)
        driver - WebDriver 的驱动程序(Ie, Firefox, Chrome 或远程)
        timeout - 最长超时时间，默认以秒为单位
        poll_frequency - 休眠时间的间隔（步长）时间，默认为 0.5 秒
        ignored_exceptions - 超时后的异常信息，默认情况下抛 NoSuchElementException 异常。
        WebDriverWait()一般由 until()或 until_not()方法配合使用，下面是 until()和 until_not()方法的说明。
        until(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值不为 False。
        until_not(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值为 False。
        lambda:
        lambda 提供了一个运行时动态创建函数的方法。
        """
        element = None
        try:
            log.logger.info('finding element: {1} , use {0}'.format(*args))
            element = self.wait.until(lambda x: x.find_element(*args), 'element not found')
            log.logger.info('element: {1} found'.format(*args))
        except TimeoutException:
            log.logger.info('element: {1} not found'.format(*args))
            print('element not found, check your locator: {1}'.format(*args))
        return element

    def find_child_element(self, webElement, *args):
        # return self.driver.find_element(*args)
        """
        这里用了显示等待WebDriverWait: 针对于某个特定的元素设置的等待时间，在设置时间内，
        默认每隔一段时间检测一次当前页面某个元素是否存在，如果在规定的时间内找到了元素，
        则直接执行，即找到元素就执行相关操作，如果超过设置时间检测不到则抛出异常。默认检测频率为0.5s。

        详细格式如下：
        WebDriverWait(driver, timeout, poll_frequency=0.5, ignored_exceptions=None)
        driver - WebDriver 的驱动程序(Ie, Firefox, Chrome 或远程)
        timeout - 最长超时时间，默认以秒为单位
        poll_frequency - 休眠时间的间隔（步长）时间，默认为 0.5 秒
        ignored_exceptions - 超时后的异常信息，默认情况下抛 NoSuchElementException 异常。
        WebDriverWait()一般由 until()或 until_not()方法配合使用，下面是 until()和 until_not()方法的说明。
        until(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值不为 False。
        until_not(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值为 False。
        lambda:
        lambda 提供了一个运行时动态创建函数的方法。
        """
        element = None
        wait = WebDriverWait(webElement, 3)
        try:
            log.logger.info('finding element: {1} , use {0}'.format(*args))
            element = wait.until(lambda x: x.find_element(*args), 'element not found')
            log.logger.info('element: {1} found'.format(*args))
        except TimeoutException:
            log.logger.info('element: {1} not found'.format(*args))
            print('element not found, check your locator: {1}'.format(*args))
        return element

    def find_elements(self, *args):
        # return self.driver.find_element(*args)
        """
        这里用了显示等待WebDriverWait: 针对于某个特定的元素设置的等待时间，在设置时间内，
        默认每隔一段时间检测一次当前页面某个元素是否存在，如果在规定的时间内找到了元素，
        则直接执行，即找到元素就执行相关操作，如果超过设置时间检测不到则抛出异常。默认检测频率为0.5s。

        详细格式如下：
        WebDriverWait(driver, timeout, poll_frequency=0.5, ignored_exceptions=None)
        driver - WebDriver 的驱动程序(Ie, Firefox, Chrome 或远程)
        timeout - 最长超时时间，默认以秒为单位
        poll_frequency - 休眠时间的间隔（步长）时间，默认为 0.5 秒
        ignored_exceptions - 超时后的异常信息，默认情况下抛 NoSuchElementException 异常。
        WebDriverWait()一般由 until()或 until_not()方法配合使用，下面是 until()和 until_not()方法的说明。
        until(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值不为 False。
        until_not(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值为 False。
        lambda:
        lambda 提供了一个运行时动态创建函数的方法。
        """
        elements = None
        try:
            log.logger.info('finding element: {1} , use {0}'.format(*args))
            elements = self.wait.until(lambda x: x.find_elements(*args), 'element not found')
            log.logger.info('element: {1} found'.format(*args))
        except TimeoutException:
            log.logger.info('element: {1} not found'.format(*args))
            print('element not found, check your locator: {1}'.format(*args))
        return elements

    def find_child_elements(self, webElement, *args):
        # return self.driver.find_element(*args)
        """
        这里用了显示等待WebDriverWait: 针对于某个特定的元素设置的等待时间，在设置时间内，
        默认每隔一段时间检测一次当前页面某个元素是否存在，如果在规定的时间内找到了元素，
        则直接执行，即找到元素就执行相关操作，如果超过设置时间检测不到则抛出异常。默认检测频率为0.5s。

        详细格式如下：
        WebDriverWait(driver, timeout, poll_frequency=0.5, ignored_exceptions=None)
        driver - WebDriver 的驱动程序(Ie, Firefox, Chrome 或远程)
        timeout - 最长超时时间，默认以秒为单位
        poll_frequency - 休眠时间的间隔（步长）时间，默认为 0.5 秒
        ignored_exceptions - 超时后的异常信息，默认情况下抛 NoSuchElementException 异常。
        WebDriverWait()一般由 until()或 until_not()方法配合使用，下面是 until()和 until_not()方法的说明。
        until(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值不为 False。
        until_not(method, message=’’)
        调用该方法提供的驱动程序作为一个参数，直到返回值为 False。
        lambda:
        lambda 提供了一个运行时动态创建函数的方法。
        """
        element = None
        wait = WebDriverWait(webElement, 3)
        try:
            log.logger.info('finding element: {1} , use {0}'.format(*args))
            element = wait.until(lambda x: x.find_elements(*args), 'element not found')
            log.logger.info('element: {1} found'.format(*args))
        except TimeoutException:
            log.logger.info('element: {1} not found'.format(*args))
            print('element not found, check your locator: {1}'.format(*args))
        return element

    def element_exist(self, *args):
        return True if self.find_element(*args) else False

    def take_screenshot(self,filename=None):
        '''
        当前window的截图，不怎么会用到，一般用元素截图就好了
        :param filename: 因为有时候有子文件夹，所以需提供完整路径
        :return:
        '''
        self.driver.get_screenshot_as_file(filename)

    def get_current_scale(self):
        '''
        获取当前的地图缩放级别
        :return: 返回整数数字，单位是米
        '''
        scale_text = self.find_element(*self.scale_locator).text
        if scale_text:
            temp = scale_text.split()
            current_scale = int(temp[0]) * 1000 if temp[1] == 'km' else int(temp[0])
            log.logger.info('current scale: {}'.format(current_scale))
            print("current_scale: ", current_scale)
            return current_scale
        else:
            return 0

    def zoom_to_scale_meters(self, scale):
        '''
        缩放到期望的级别(scale)
        :param scale: 参数单位是米
        :return:
        '''
        # allowed_scale = np.array([5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000])
        # numpy is faster, but as our array is short and operation is simple, no need to use it
        allowed_scale = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
        try:
            dest_index = allowed_scale.index(int(scale))
            current_scale_index = allowed_scale.index(self.get_current_scale())
            while dest_index < current_scale_index:
                self.find_element(*self.zoom_in_locator).click()
                self.get_current_scale()
                current_scale_index = current_scale_index - 1
            while dest_index > current_scale_index:
                self.find_element(*self.zoom_out_locator).click()
                self.get_current_scale()
                current_scale_index = current_scale_index + 1
        except ValueError:
            log.logger.info('scale {} not allowed!'.format(scale))
            print('scale {} not allowed!'.format(scale))

    def click_canvas_by_image(self, canvas_image_name, tpl_image_name):
        canvas_image_name = self.take_screenshot_element(self.find_element(*self.map_canvas_locator), canvas_image_name)#先截个当前canvas的图
        path_current_directory = os.path.dirname(os.path.dirname(__file__))
        tpl_image_name = config.get_config('SCREENSHOT', 'SCREENSHOT_PATH') + tpl_image_name
        tpl_image_name = os.path.join(path_current_directory, tpl_image_name)
        print(canvas_image_name,tpl_image_name)

        xy = color_match_diff_scale(canvas_image_name, tpl_image_name, False) #获取模板图像的坐标
        self.click_map_canvas_by_xy(*xy) #点击该坐标



    '''
    def element_enabled(self,element):
        return element.is_enabled()

    def element_enabled(self, element):
        return element.is_displayed()
    '''
