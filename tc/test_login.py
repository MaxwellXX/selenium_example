import sys
import traceback
from time import sleep
from util.my_exception import ElementNotFoundException
from pages.login_page import LoginPage
import pytest
import logging
import os
from selenium import webdriver
from util.log import Logger
from util.config import Config

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()
LOGIN_URL = config.get_config('DEV','LOGIN') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','LOGIN')
USER = config.get_config('DEV','USER') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','USER')
PWD = config.get_config('DEV','PWD') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','PWD')

class TestLogin(object):

    def get_driver(self):
        path_current_directory = os.path.dirname(os.path.dirname(__file__))
        driver_path_from_config = config.get_config('DRIVER', 'DRIVER_PATH')
        driver_path = os.path.join(path_current_directory, driver_path_from_config)
        # open chrome browser
        driver = webdriver.Chrome(executable_path=driver_path)
        driver.get(LOGIN_URL)
        return driver

    def test_login_invalid_user(self):
        log.logger.info('==========================test login with invalid username,pwd==========================')
        driver = self.get_driver()
        lp = LoginPage(driver)
        sleep(1)
        try:
            lp.login('aaaa', 'silverx')
            # get_attribute() and text both works
            assert "Invalid email or password" in lp.get_loginFail().get_attribute("innerHTML")
            log.logger.info('assert login fail text: {}, should contain '', result: {}'.format(lp.get_loginFail().get_attribute("innerHTML"),"Invalid email or password" in lp.get_loginFail().text))
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
            driver.quit()


    def test_login_valid_user(self):
        log.logger.info('==========================test login with valid username,pwd==========================')
        driver = self.get_driver()
        lp = LoginPage(driver)
        sleep(1)
        # lp.take_screenshot('driverOK1')
        try:
            lp.login(USER, PWD)
            assert lp.get_loginUser().is_displayed()
            log.logger.info('assert login user is displayed, result: {}'.format(lp.get_loginUser().is_displayed()))
            assert lp.get_loginUser().text in 'App Test1  app1   '
            log.logger.info(
                'assert login user name is displayed in right upside, result: {}'.format('App Test1' in lp.get_loginUser().text))
        except ElementNotFoundException as e:
            pytest.fail('cannot find some elements, please see log for details!')
            sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            driver.quit()

    def test_logout(self):
        log.logger.info('==========================test log out==========================')
        driver = self.get_driver()
        lp = LoginPage(driver)
        sleep(1)
        # lp.take_screenshot('driverOK1')
        try:
            lp.login(USER, PWD)
            # getAttribute("innerHTML") not working
            assert lp.get_loginUser().text in 'App Test1    app1   '
            log.logger.info(
                'assert login user name is displayed in right upside, result: {}'.format(
                    'App Test1' in lp.get_loginUser().text))

            lp.logout()
            assert lp.get_loginBtn().is_displayed()
            log.logger.info(
                'assert login button is displayed, result: {}'.format(
                    lp.get_loginBtn().is_displayed()))
        except ElementNotFoundException:
            pytest.fail('cannot find some element, please see log for details!')
            sys.exit()
        except AssertionError:
            _, _, tb = sys.exc_info()
            traceback.print_tb(tb)  # Fixed format
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            log.logger.info('An error occurred on line {} in statement {}'.format(line, text))
            print('An error occurred on line {} in statement {}'.format(line, text))
            driver.quit()
            # exit(1)
