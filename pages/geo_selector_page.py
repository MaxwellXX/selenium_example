import logging
from time import sleep
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from util.log import Logger
from util.config import Config

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
config = Config()

log = Logger(__name__, CmdLevel=logging.INFO, FileLevel=logging.INFO)
c = Config()


class GeoSelector(BasePage):
    def __init__(self,driver):
        super().__init__(driver)
        self.geo_selector_icon_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(1) > nav > div > ul:nth-child(6) > li > a > img.nimg2")
        self.geo_selector_clicked_icon_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(1) > nav > div > ul:nth-child(6) > li > a > img.nimg1")
        self.geo_selector_shanghai_locator = (By.CSS_SELECTOR, "body > div.page-body > div:nth-child(1) > nav > div > ul:nth-child(6) > li > ul > li > div > div.context > section.city-hotlist.clearfix.ng-scope > ul > li:nth-child(5) > a.fa.fa-map-marker")
        self.map_center_locator = (By.CSS_SELECTOR, "#project-map > div.ol-city-info.ng-scope > span:nth-child(1) > b")

    def get_geo_selector_icon(self):
        return self.find_element(*self.geo_selector_icon_locator)

    def get_geo_selector_clicked_icon(self):
        return self.find_element(*self.geo_selector_clicked_icon_locator)

    def get_geo_selector_shanghai(self):
        return self.find_element(*self.geo_selector_shanghai_locator)

    def get_map_canvas(self):
        return self.find_element(*self.map_canvas_locator)

    def get_map_center(self):
        return self.find_element(*self.map_center_locator)

    def open_geo_selector(self):
        if self.element_exist(*self.geo_selector_icon_locator):
            self.get_geo_selector_icon().click()
            log.logger.info('clicked geo_selector_icon_locator button ')

    def jump_to_shanghai(self):
        if self.element_exist(*self.geo_selector_shanghai_locator):
            self.get_geo_selector_shanghai().click()
            log.logger.info('clicked get_geo_selector_shanghai_locator ')
            self.click_map_canvas_by_xy(500, 225)
            # only when mouse is moved to map, will map center be changed
            log.logger.info('clicked map ')