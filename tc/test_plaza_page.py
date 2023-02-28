import logging
import pytest
import sys
import traceback
from time import sleep
from util.log import Logger
from util.config import Config
from util.my_exception import ElementNotFoundException
from util.util import read_tuple_yaml
from pages.plaza_page import plazaPage
from selenium.webdriver.common.by import By

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()
WORKSPACE_URL = config.get_config('DEV','WORKSPACE') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','WORKSPACE')

index = 0

class TestplazaLayer(object):
    @pytest.mark.dependency()
    def test_close_all_plaza_layers(self, chrome_driver, get_login_page):
        log.logger.info('==========================test close all plaza layers==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        vp = plazaPage(chrome_driver)
        sleep(1)
        try:
            vp.close_all_plaza_layers_by_source()
            sleep(1)
            # get all plaza layer's open status and convert to set
            status = set(o['opened'] for o in vp.get_plaza_layers_open_status())
            # assert that all are closed, closed == False
            assert len(status) == 1 and status == {False}
            log.logger.info('assert all layer closed'', result: {}'.format(len(status) == 1 and status == {False}))
        except ElementNotFoundException as e:
             pytest.fail('cannot find some element, please see log for details!')
             sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            chrome_driver.quit()

    @pytest.mark.dependency(depends=["test_close_all_plaza_layers"])
    def test_open_the_first_plaza_layer_filters_chn_eng(self, chrome_driver, get_login_page):
        log.logger.info('==========================test open the first plaza layer''s filters==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        vp = plazaPage(chrome_driver)
        sleep(3)
        try:
            # double click to open
            vp.open_plaza_filters_by_index(0)
            sleep(1)
            # reset filters
            vp.reset_filter()
            # take a screenshot of default filter
            vp.find_element(By.CLASS_NAME, 'query-thumbnail').screenshot(
                '../screen/plaza_layer/default_filter_expect.png')
            vp.get_map_canvas().screenshot(
                '../screen/plaza_layer/default_canvas.png')
            curr_language = vp.get_current_languge()
            status = vp.get_plaza_layers_open_status()

            test_data = read_tuple_yaml('../data/plaza_layer_filters.yaml')
            for data in test_data:
                print('data: ', data)
                # get child filter's text
                text = vp.get_child_filter_text(data['title'], data['filter_type'], data['txt_find_from'], data['txt_locator'])
                expected = data['txt_eng'] if curr_language == 'ENG' else data['txt_chn']
                print('expected: ',expected)
                print('text: ', text)

                if data['assertion_type'] == 'identical':
                    # 判断两个数组内容和顺序完全一样
                    result = (len(text) == len(expected) and len(text) == sum(
                    [1 for i, j in zip(text, expected) if i == j]))
                    log.logger.info('assert array identical, text: {}, expected: {}, result: {}'.format(text, expected, result))
                elif data['assertion_type'] == 'partial_single':
                    # 判断text的第一个元素取值只能是True
                    re = set(e in text[0] for e in expected)
                    result = len(re) ==1 and True in re
                    log.logger.info('assert only True, text: {}, expected: {}, result: {}'.format(text, expected, result))
                elif data['assertion_type'] == 'partial_all':
                    # 判断text一一包含expected
                    result = (len(text) == len(expected) and len(text) == sum(
                        [1 for i, j in zip(text, expected) if j in i]))
                    log.logger.info('assert text contains expected, text: {}, expected: {}, result: {}'.format(text, expected, result))
                assert result
        except ElementNotFoundException as e:
             pytest.fail('cannot find some element, please see log for details!')
             sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            chrome_driver.quit()

    def test_in_layer_search(self, chrome_driver, get_login_page):
        log.logger.info('==========================test in layer search==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        vp = plazaPage(chrome_driver)
        sleep(3)
        try:
            # double click to open
            vp.open_plaza_filters_by_index(0)
            sleep(1)
            # reset filters
            vp.do_in_layer_search('plaza_1')
            vp.get_in_layer_search_result().screenshot(
                '../screen/plaza_layer/in_layer_expect.png')
            vp.get_in_layer_search_result().click()

            img_loaded = vp.get_plaza_detail_facade_photo_load_status()
            curr_language = vp.get_current_languge()

            test_data = read_tuple_yaml('../data/plaza1.yaml')
            for data in test_data:
                for ele in data['elements']:
                    print(ele['locator'])
                    locator = (eval(ele['locator'][0]), ele['locator'][1])
                    elements = vp.find_elements(*locator)
                    text = list(txt.get_attribute("innerText") for txt in elements)

                    expected = list((et[0] for et in ele['text']) if curr_language == 'CHN' else (et[1] for et in ele['text']))
                    print('text: {}, expected: {}'.format(text, expected))
                    result = (len(text) == len(expected) and len(text) == sum(
                        [1 for i, j in zip(text, expected) if j in i]))
                    log.logger.info('assert text contains expected, text: {}, expected: {}, result: {}'.format(text, expected, result))

            assert img_loaded
            assert result
        except ElementNotFoundException as e:
             pytest.fail('cannot find some element, please see log for details!')
             sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            chrome_driver.quit()


    def test_click_plaza_poi_on_map(self, chrome_driver, get_login_page):
        log.logger.info('==========================test click poi on map==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        vp = plazaPage(chrome_driver)
        sleep(3)
        try:
            # double click to open
            vp.open_plaza_filters_by_index(0)
            sleep(1)
            # reset filters
            vp.do_in_layer_search('plaza_1')
            vp.get_in_layer_search_result().click()
            sleep(2) # 强制等待
            vp.zoom_to_scale_meters(500)
            vp.click_canvas_by_image('plaza_layer/plaza_1-canvas.png', 'plaza_layer/广场1.png')

            img_loaded = vp.get_plaza_detail_facade_photo_load_status()
            curr_language = vp.get_current_languge()

            test_data = read_tuple_yaml('../data/plaza1.yaml')
            for data in test_data:
                for ele in data['elements']:
                    print(ele['locator'])
                    locator = (eval(ele['locator'][0]), ele['locator'][1])
                    elements = vp.find_elements(*locator)
                    text = list(txt.get_attribute("innerText") for txt in elements)

                    expected = list(
                        (et[0] for et in ele['text']) if curr_language == 'CHN' else (et[1] for et in ele['text']))
                    print('text: {}, expected: {}'.format(text, expected))
                    result = (len(text) == len(expected) and len(text) == sum(
                        [1 for i, j in zip(text, expected) if j in i]))
                    log.logger.info(
                        'assert text contains expected, text: {}, expected: {}, result: {}'.format(text, expected,
                                                                                                   result))

            assert img_loaded
            assert result
        except ElementNotFoundException as e:
            pytest.fail('cannot find some element, please see log for details!')
            sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            chrome_driver.quit()