import logging
import os
from time import sleep
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from util.log import Logger
from util.config import Config

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()

HOST = config.get_config('DEV', 'HOST') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'HOST')
LOGIN_URL = config.get_config('DEV', 'LOGIN') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'LOGIN')
WORKSPACE_URL = config.get_config('DEV', 'WORKSPACE') if config.get_config('DEFAULT','DEBUG') == 'True' else config.get_config('PRD', 'WORKSPACE')

class LayerPage(BasePage):
    def __init__(self, driver, map_source):
        super().__init__(driver)
        self.map_source = map_source
        #self.filter_elements_locator = (By.CSS_SELECTOR, "div[class^='qthumnail-item'][title]") why this locator doesn't work?
        self.filter_elements_locator = (By.CSS_SELECTOR, "div[class^='qthumbnail-item']")

        self.filter_explain_locator = (By.CSS_SELECTOR, "div[class='qt-explain']>div[class^='qt-explain-txt']")
        #element>element div > p	Selects all <p> elements where the parent is a <div> element
        self.in_layer_search_inputbox_locator = (By.CSS_SELECTOR, "div[class='navbar-search-ipt']>input")
        #element+element div + p	Selects all <p> elements that are placed immediately after <div> elements

        self.poi_detail_locator = (By.ID,"lhs-context")
        self.poi_detail_close_locator = (By.CSS_SELECTOR, "div[class='lhs-uiview-close']")

    def get_layer_group_only_by_source(self):
        '''
        获取某种map_source的图层组，返回值是一个webelement
        return only the parent group that has all layers
        '''
        if not self.map_source :
            raise AttributeError('no map_source provided!')
        if self.map_source not in """global_plazas global_buildings global_stores target_store global_rating_clusters
                        global_icl_poi global_icl_public_transport geo_layer global_demographic nike_tradezone""":
            raise AttributeError('invalid type: {}'.format(self.map_source))
        else:
            selector = "#drag_list>li[class='ng-scope layer_group_" + self.map_source + " lg-multiple']>div[class='layer_group layer-group']"
            return self.find_element(By.CSS_SELECTOR, selector)

    def get_all_layers_in_group_by_source(self):
        '''
        获取某种map_source所有图层，返回值是图层列表webelement list
        :param type:
        :return: all layers including the last  ... button
        '''
        if not self.map_source:
            raise AttributeError('no map_source provided!')
        if self.map_source not in """global_plazas global_buildings global_stores target_store global_rating_clusters
                        global_icl_poi global_icl_public_transport geo_layer global_demographic nike_tradezone""":
            raise AttributeError('invalid type: {}'.format(self.map_source))
        else:
            selector = "#drag_list>li[class='ng-scope layer_group_" + self.map_source + " lg-multiple']>div[class='layer_group layer-group']>div"
            # selector = "#drag_list>li>div>div" # this selector will select all layers in workspace
            return self.find_elements(By.CSS_SELECTOR, selector)

    def get_all_layers_img_in_group_by_source(self):
        '''
            获取某种map_source所有图层的图片元素，返回值是图片webelement list
            :param type:
            :return: including the last  ... button img
        '''
        if not self.map_source:
            raise AttributeError('no map_source provided!')
        if self.map_source not in """global_plazas global_buildings global_stores target_store global_rating_clusters
                                global_icl_poi global_icl_public_transport geo_layer global_demographic nike_tradezone""":
            raise AttributeError('invalid type: {}'.format(self.map_source))
        else:
            selector = "#drag_list>li[class='ng-scope layer_group_" + self.map_source + " lg-multiple']>div[class='layer_group layer-group']>div"
            # selector = "#drag_list>li>div>div" # this selector will select all layers in workspace
            return self.find_elements(By.CSS_SELECTOR, selector)

    def get_layers_open_status(self, img_name):
        '''
            get all  layers' open status
            :param img_name when layer is open
            check if unhided and hided layer's src is the yellow colored img, if yes, return 1.
            :return: layer index, open status 1 or 0
        '''
        # get image attribute of all layers
        layer_status = list()
        print('map_source map_source map_source :', self.map_source)
        all_layer_img = self.get_all_layers_img_in_group_by_source()
        print('all_layer_img all_layer_img: ', len(all_layer_img), all_layer_img)
        for index, img in enumerate(all_layer_img):
            # print(type(all_layers[i]))
            if index < (len(all_layer_img)-1): # skip the last one
                layer_status.append(
                {"layer": index, "opened": True if self.layer_img_same(img, img_name) else False})
        # print(layer_status)
        return layer_status

    def get_layers_image_load_status(self):
        '''
        see if all plaza layers' image are loaded successfully
        :param all_layers_image:
        run a js script to see image is displayed, if yes, return 1
        :return: layer index, open status 1 or 0
        '''
        img_load_status = list()
        for i,img in enumerate(self.get_all_layers_img_in_group_by_source()):
            img_load_status.append({"layer": i, "loaded": 1 if self.image_loaded(img) else 0})
        return img_load_status

    def open_layer_by_index(self, index ,img_name):
        layer_status = self.get_layers_open_status(img_name)
        all_layers = self.get_all_layers_in_group_by_source()

        if index > len(layer_status):
            raise OverflowError('index out of range!')
        if layer_status[index] is True:
            raise AttributeError('the layer is already opened!')
        else:
            all_layers[index].click()

    def open_filters_by_index(self, index, img_name):
        '''
        双击打开某个图层的filter
        create action chain object
        double click the item
        perform the operation
        '''
        layer_status = self.get_layers_open_status(img_name)
        all_layers = self.get_all_layers_in_group_by_source()

        if index > len(layer_status):
            raise OverflowError('index out of range!')
        else:
            action = ActionChains(self.driver)
            action.double_click(on_element=all_layers[index])
            action.perform()
            sleep(3) # 加载图片要时间，强制等待一下

    def get_child_filter_text(self, parent_title, filter_type,  find_from, child_locator):
        curr_language = self.get_current_languge()
        print('current language1: {}'.format(curr_language))
        if filter_type == 'regular':
            self.click_filter_by_title(*parent_title)
        elif filter_type == 'complex':
            self.click_filter_by_title('高级过滤', 'Complex Filter')
            parent_loc = (eval(parent_title[0]), parent_title[1])
            self.click_complex_filter(parent_loc)
        sleep(2)
        child_loc = (eval(child_locator[0]), child_locator[1])
        print('child_locator: ', child_loc)
        children = None
        if find_from == 'parent':
            children = self.find_child_elements(self.get_filter_element_by_title(*parent_title), *child_loc)
        else:
            children = self.find_elements(*child_loc)

        if filter_type == 'complex':
            # close the opened complex filter
            self.click_filter_by_title('高级过滤', 'Complex Filter')
        return list(txt.get_attribute("innerText") for txt in children)


    def get_filter_text_chn_eng(self):
        curr_language = self.get_current_languge()
        print('current language1: {}'.format(curr_language))
        '''
        no need to check against source, use screenshot is enough
        imgs = self.find_elements(*self.filter_image_locator)
        img_list = list()
        for i in imgs:
            if i.get_attribute('aria-expanded') == 'true':
                img = self.find_child_element(i, By.XPATH, ".//img[@class='qt-img2']")
                img_list.append(img.get_attribute('src'))
            else:
                img = self.find_child_element(i, By.XPATH, ".//img")
                img_list.append(img.get_attribute('src'))
        print(len(img_list),img_list)
        '''
        explains = self.find_elements(*self.filter_explain_locator)
        explain_eng = list()
        explain_chn = list()
        if curr_language == 'ENG':
            print('1, processing eng..')
            explain_eng = list(txt.get_attribute("innerText") for txt in explains)
        else:
            explain_chn = list(txt.get_attribute("innerText") for txt in explains)
            print('2, processing chn..')

        self.change_languge()
        curr_language = self.get_current_languge()
        print('current language2: {}'.format(curr_language))
        if curr_language == 'ENG':
            explain_eng = list(txt.get_attribute("innerText") for txt in explains)
        else:
            explain_chn = list(txt.get_attribute("innerText") for txt in explains)
        print(curr_language,len(explain_chn),explain_chn,len(explain_eng),explain_eng)

        return {"explain_chn": explain_chn ,"explain_eng": explain_eng}

    def layer_img_same(self, layer_element, img_name):
        '''
        根据显示的图标检查某种类型的layer是否是打开(高亮)/非高亮状态
        :param map_source:
        :param layer_element:
        :return:
        '''
        layer_image_child_locator = (By.XPATH, ".//div/*[@class='layer-thumbnail']/img")
        img = HOST + img_name
        return True if self.find_child_element(layer_element, *layer_image_child_locator).get_attribute("src") == img else False

    def get_filter_elements(self):
        '''
        获取当前打开图层的所有filter, 返回值是webelement list
        :return: filters' element as a list
        '''
        return self.find_elements(*self.filter_elements_locator)

    def get_filter_element_by_title(self, title_chn, title_eng):
        '''
        获取某个图层，某个title的filter(根据title获取filter), 返回值是single webelement
        :param layer_element, filter title
        :return: single filter element
        '''
        se = "div[class^='qthumbnail-item'][title='"+title_chn+"'],div[class^='qthumbnail-item'][title='"+title_eng+"']"
        selector = (By.CSS_SELECTOR, se)
        return self.find_element(*selector)

    def get_complex_filter_element_by_title(self, title_chn, title_eng):
        '''
        获取某个图层，complex filter下，某个title的filter(根据title获取filter), 返回值是single webelement
        :param layer_element, filter title
        :return: single filter element
        这个locator不知道为什么有问题，换成用id了
        '''
        # driver.find_element(By.XPATH, '//button[text()="Some text"]')
        #se = "div[class=filter-container]>div.filter-context > div[class='filter short dropdown dropdown-toggle'] > span[class^='filter-title'][text() = '"+title_eng+"'],"
        se = "div[class='filter short dropdown dropdown-toggle'] > span[class^='filter-title'][text() *= '" + title_chn + "'],div[class='filter short dropdown dropdown-toggle'] > span[class^='filter-title'][text() *= '" + title_eng + "']"
        selector = (By.CSS_SELECTOR, se)
        return self.find_element(*selector)

    def click_filter_by_title(self,title_chn, tile_eng):
        self.get_filter_element_by_title(title_chn, tile_eng).click()

    def click_complex_filter_by_title(self, title_chn, tile_eng):
        self.get_complex_filter_element_by_title(title_chn, tile_eng).click()

    def click_complex_filter(self, locator):
        self.find_element(*locator).click()

    def get_filter_element_by_element_and_title(self, filter_element, title_chn, title_eng):
        '''
        获取某个图层，某个title的filter(根据title获取filter), 返回值是single webelement
        :param layer_element, filter title
        :return: single filter element
        '''
        if self.get_current_languge() == 'ENG':
            return self.find_child_element(filter_element, By.PARTIAL_LINK_TEXT, title_eng)
        else:
            return self.find_child_element(filter_element, By.PARTIAL_LINK_TEXT, title_chn)

    def reset_filter(self):
        layer_all_filters = self.get_filter_elements()
        more_button_index = len(layer_all_filters) - 3
        # more_button = layer_all_filters[more_button_index]
        # print(more_button_index, more_button.get_attribute("title"))
        # more_button.click()
        more_button = self.get_filter_element_by_title('更多', 'More')
        more_button.click()
        print('clicked more_button, ', more_button.get_attribute("title"))
        sleep(2)
        self.get_filter_element_by_element_and_title(more_button,'恢复默认过滤','Reset Filter').click()
        more_button.click()
        self.click_map_canvas_by_xy(400,500) # close more filter

    def do_in_layer_search(self, keyword):
        self.click_filter_by_title('搜索','Search')
        self.find_element(*self.in_layer_search_inputbox_locator).send_keys(keyword)
        sleep(1)

    def get_in_layer_search_result(self):
        in_layer_search_result_locator = (By.CSS_SELECTOR, "div[class='search-results']>div[class^='item']")
        return self.find_element(*in_layer_search_result_locator)

    def get_poi_detail(self):
        return self.find_element(*self.poi_detail_locator)

    def close_poi_detail(self):
        self.find_element(*self.poi_detail_close_locator).click()

    def close_layers_in_layer_list(self, layer_status):
        all_layers = self.get_all_layers_in_group_by_source()
        layer_count = len(layer_status)
        all_layers[layer_count].click()  # open layer list
        layer_list_locator = (By.CSS_SELECTOR,
                              "div[class='body_to_div']>div[class='layer-more-group layer_more_group']>div[class='lmg-ul lmg_ul']>div[class^='lmg-li']")

        layer_list = self.find_elements(*layer_list_locator)  # find out all layers in layer list
        for layer in layer_status:
            if layer['opened'] is True:
                # print(layer['layer'])
                layer_list[layer['layer']].click()
                sleep(1)

        all_layers[layer_count].click()  # close layer list

    def close_all_laysers_in_workspace(self):
        pass


