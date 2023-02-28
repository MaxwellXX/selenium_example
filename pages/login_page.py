import logging
from time import sleep
from pages.base_page import BasePage
from selenium.webdriver.common.by import By

from util.log import Logger
from util.config import Config
from util.my_exception import ElementNotFoundException

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
c = Config()


class LoginPage(BasePage):
    def __init__(self,driver):
        super().__init__(driver)
        self.user_name_locator = (By.CSS_SELECTOR, "body > div > div:nth-child(3) > div > form > input:nth-child(1)")
        self.user_pwd_locator = (By.CSS_SELECTOR, "body > div > div:nth-child(3) > div > form > input:nth-child(2)")
        self.login_btn_locator = (By.CSS_SELECTOR, "body > div > div:nth-child(3) > div > form > button")
        self.auto_login_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(3) > div > form > div.lp-btns.clearfix > div.auto-login.checkbox > label > input")
        self.forgot_pwd_locator = (By.LINK_TEXT, "Forgot password?")
        self.login_fail_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(3) > div > form > div.alert-danger.ng-isolate-scope.alert.alert-dismissible > div > span")
        self.login_user_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(1) > nav > div > ul:nth-child(2) > li > a")

    @property
    def logout_btn_locator(self):
        return (By.PARTIAL_LINK_TEXT, "Logout") if self.get_current_languge() == 'ENG' else (By.PARTIAL_LINK_TEXT, "退出")

    def get_user_name(self):
        return self.find_element(*self.user_name_locator)

    def get_user_pwd(self):
        return self.find_element(*self.user_pwd_locator)

    def get_login_btn(self):
        return self.find_element(*self.login_btn_locator)

    def get_login_user(self):
        return self.find_element(*self.login_user_locator)

    def get_logout_btn(self):
        return self.find_element(*self.logout_btn_locator)

    def get_login_fail(self):
        sleep(1) # hard wait for error message to be shown
        return self.find_element(*self.login_fail_locator)

    def login(self,user, pwd):
        '''
        will never happen !
        if self.element_exist(*self.login_user_locator):
            # self.take_screenshot('loginUser')
            self.logout()
            sleep(1)
            log.logger.info('user automatically login, firstly logout ')
        '''
        if self.element_exist(*self.login_btn_locator):
            self.get_user_name().clear()
            self.get_user_name().send_keys(user)
            self.get_user_pwd().clear()
            self.get_user_pwd().send_keys(pwd)
            self.get_login_btn().click()
            log.logger.info('clicked login button ')
            sleep(5)
        else:
            log.logger.info('some error happen, unable to logout ')
            raise ElementNotFoundException('login button not found!')

    def logout(self):
        if self.element_exist(*self.login_user_locator):
            self.get_login_user().click()
            sleep(1)
            self.get_logout_btn().click()
            log.logger.info('clicked logout button ')
        else:
            log.logger.info('some error happen, unable to logout ')
            raise ElementNotFoundException('current user not found!')

