import logging
import pytest
import sys
import traceback
from time import sleep
from util.log import Logger
from util.config import Config
from util.my_exception import ElementNotFoundException
from pages.geo_selector_page import GeoSelector

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()
WORKSPACE_URL = config.get_config('DEV','WORKSPACE') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','WORKSPACE')

class TestGeoSelector(object):

    def test_open_geo_selector(self, chrome_driver, get_login_page):
        log.logger.info('==========================test open geo selector==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        gs = GeoSelector(chrome_driver)
        sleep(1)
        try:
            gs.open_geo_selector()
            sleep(1)

            # get_attribute() and text both works
            assert gs.get_geo_selector_clicked_icon().is_displayed()
            log.logger.info('assert geo selector is yellow '', result: {}'.format(gs.get_geo_selector_clicked_icon().is_displayed()))
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

    def test_jump_to_city(self, chrome_driver, get_login_page):
        log.logger.info('==========================test open geo selector==========================')
        chrome_driver.get(WORKSPACE_URL)
        log.logger.info('open xxx workspace page')
        gs = GeoSelector(chrome_driver)
        sleep(1)
        try:
            gs.open_geo_selector() # open geoSelector
            gs.jump_to_shanghai() # go to shanghai
            sleep(1)
            assert gs.get_map_center().text in 'ShangHai Shi 上海市'
            log.logger.info('assert geo selector is yellow '', result: {}'.format(gs.get_geo_selector_clicked_icon().is_displayed()))
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