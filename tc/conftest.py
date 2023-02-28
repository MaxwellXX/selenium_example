import pytest
import logging
import os
from time import sleep
from selenium import webdriver
from util.log import Logger
from util.config import Config
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()
LOGIN_URL = config.get_config('DEV','LOGIN') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','LOGIN')
USER = config.get_config('DEV','USER') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','USER')
PWD = config.get_config('DEV','PWD') if config.get_config('DEFAULT', 'DEBUG') == 'True' else config.get_config('PRD','PWD')
global driver

@pytest.fixture(scope="function")
def chrome_driver():
    # get chrome driver path
    path_current_directory = os.path.dirname(os.path.dirname(__file__))
    driver_path_from_config = config.get_config('DRIVER', 'DRIVER_PATH')
    driver_path = os.path.join(path_current_directory, driver_path_from_config)
    # open chrome browser
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path=driver_path)
    driver.maximize_window()
    log.logger.info('setup chrome driver')
    yield  driver
    driver.quit()
    log.logger.info('quit chrome driver')


@pytest.fixture(scope="function")
def get_login_page(chrome_driver):
    chrome_driver.get(LOGIN_URL)
    LoginPage(chrome_driver).login(USER, PWD)
    sleep(1)
    yield
    LoginPage(chrome_driver).logout()


