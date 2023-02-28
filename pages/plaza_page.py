import logging
import os
from time import sleep
from pages.layer_page import LayerPage
from pages.login_page import LoginPage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from util.log import Logger
from util.config import Config

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()

HOST = config.get_config('DEV', 'HOST') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'HOST')
LOGIN_URL = config.get_config('DEV', 'LOGIN') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'LOGIN')
WORKSPACE_URL = config.get_config('DEV', 'WORKSPACE') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'WORKSPACE')

class plazaPage(LayerPage):
    def __init__(self,driver):
        super().__init__(driver, map_source="global_plazas")
        self.plaza_layer_image_show = "/images/limg_plazas01.b6034ee.png"
        self.plaza_layer_image_hide = "/images/limg_plazas02.9799c30.png"

    def is_layer_open(self, layer_element):
        return self.layer_img_same(layer_element, self.plaza_layer_image_show)

    def is_layer_hide(self, layer_element):
        return self.layer_img_same(layer_element, self.plaza_layer_image_hide)

    def get_plaza_layers_open_status(self):
        return self.get_layers_open_status(self.plaza_layer_image_show)

    def open_plaza_layer_by_index(self, index):
        self.open_layer_by_index(index, self.plaza_layer_image_show)

    def open_plaza_filters_by_index(self, index):
        self.open_filters_by_index(index, self.plaza_layer_image_show)

    def close_all_plaza_layers_by_source(self):
        '''
        close all layers before doing something
        :param layer_status:
        :return:
        '''
        layer_image = self.get_all_layers_img_in_group_by_source()
        layer_status = self.get_plaza_layers_open_status()
        layer_count = len(layer_status)
        # print(layer_count, layer_status)
        show_count = sum(list(ls['opened'] for ls in layer_status))
        if layer_count < 6 and show_count > 0:
            for layer in layer_status:
                if layer['opened'] is True:
                    layer_image[layer['layer']].click()  # just click opened ones in layer container
        elif layer_count >= 6 and show_count > 0 :
            self.close_layers_in_layer_list(layer_status)

    def get_plaza_detail_facade_photo_load_status(self):
        facade_locator = (By.CSS_SELECTOR, "div[class='photo-container']>div>div>div>div>img")
        return self.image_loaded(self.find_element(*facade_locator))

    def get_plaza_detail_chn_text(self):
        if self.get_current_languge() == 'ENG':
            self.change_languge()

if __name__ == '__main__':
    path_current_directory = os.path.dirname(os.path.dirname(__file__))
    driver_path_from_config = config.get_config('DRIVER', 'DRIVER_PATH')
    driver_path = os.path.join(path_current_directory, driver_path_from_config)
    print(driver_path)
    # open chrome browser
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path=driver_path)
    driver.maximize_window()
    driver.get(LOGIN_URL)
    lp = LoginPage(driver)
    lp.login('annxxx', 'colorful')
    #lp.login('app1', 'nikola')
    driver.get(WORKSPACE_URL)
    vp = plazaPage(driver)
    sleep(2)
    al = vp.get_all_layers_in_group_by_source()
    ali = vp.get_all_layers_img_in_group_by_source()
    print(len(al), al[0].get_attribute('title'),len(ali), ali[0].get_attribute('src') )
    print(vp.is_layer_open(al[0]), vp.is_layer_hide(al[0]))
    print(vp.get_user_map_sources())
    vp.close_all_layers_by_source()
    print('close all plaza layers')
    sleep(3)
    vp.open_plaza_filters_by_index(0)
    vp.take_screenshot_element(vp.get_map_canvas(),'/plaza_layer/open_filters.png')
    #vp.reset_filter()
    vp.click_filter_by_title('帮助说明','Explanation')
    print(vp.get_default_filter_icon_and_text_chn_eng())
    vp.do_in_layer_search('plaza1')
    vp.get_in_layer_search_result().click()

    sleep(2) # force wait as facade photo might be loading
    vp.close_poi_detail()
    sleep(2)
    vp.click_canvas_by_image('plaza_layer/plaza1-canvas.png','plaza_layer/xxx.png')
    sleep(2)
    vp.take_screenshot_element(vp.get_poi_detail(),'/plaza_layer/poi_detail1.png')
    driver.execute_script("return arguments[0].scrollIntoView(true);", vp.get_poi_detail())
    vp.take_screenshot_element(vp.get_poi_detail(), '/plaza_layer/poi_detail2.png')
    vp.zoom_to_scale_meters(500)
    sleep(2)

    lp.logout()
    driver.quit()
