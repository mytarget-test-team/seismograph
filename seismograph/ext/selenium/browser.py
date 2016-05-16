# -*- coding: utf-8 -*-

from .proxy import WebDriverProxy


DEFAULT_WAIT_TIMEOUT = None
DEFAULT_POLLING_TIMEOUT = 10
DEFAULT_POLLING_DELAY = None
DEFAULT_LOAD_PAGE_TIMEOUT = 10
DEFAULT_SCRIPT_TIMEOUT = None
DEFAULT_MAXIMIZE_WINDOW = True
DEFAULT_WINDOW_SIZE = None


def create(selenium, driver):
    browser = WebDriverProxy(
        driver,
        config=BrowserConfig(selenium, driver),
    )
    browser.reason_storage['browser name'] = selenium.browser_name
    return browser


class BrowserConfig(object):

    def __init__(self, selenium, driver):
        self.__driver = driver

        self.PROJECT_URL = selenium.config.get('PROJECT_URL')

        self.POLLING_DELAY = selenium.config.get(
            'POLLING_DELAY', DEFAULT_POLLING_DELAY,
        )
        self.POLLING_TIMEOUT = selenium.config.get(
            'POLLING_TIMEOUT', DEFAULT_POLLING_TIMEOUT,
        )

        self.__PAGE_LOAD_TIMEOUT = None
        self.PAGE_LOAD_TIMEOUT = selenium.config.get(
            'PAGE_LOAD_TIMEOUT', DEFAULT_LOAD_PAGE_TIMEOUT,
        )

        self.__SCRIPT_TIMEOUT = None
        self.SCRIPT_TIMEOUT = selenium.config.get(
            'SCRIPT_TIMEOUT', DEFAULT_SCRIPT_TIMEOUT,
        )

        self.__WAIT_TIMEOUT = None
        self.WAIT_TIMEOUT = selenium.config.get(
            'WAIT_TIMEOUT', DEFAULT_WAIT_TIMEOUT,
        )

        self.__WINDOW_SIZE = None
        self.WINDOW_SIZE = selenium.config.get(
            'WINDOW_SIZE', DEFAULT_WINDOW_SIZE,
        )

        self.__MAXIMIZE_WINDOW = False
        self.MAXIMIZE_WINDOW = selenium.config.get(
            'MAXIMIZE_WINDOW', DEFAULT_MAXIMIZE_WINDOW,
        )

    @property
    def PAGE_LOAD_TIMEOUT(self):
        return self.__PAGE_LOAD_TIMEOUT

    @PAGE_LOAD_TIMEOUT.setter
    def PAGE_LOAD_TIMEOUT(self, value):
        self.__PAGE_LOAD_TIMEOUT = value
        self.__driver.set_page_load_timeout(value or 0)

    @property
    def SCRIPT_TIMEOUT(self):
        return self.__SCRIPT_TIMEOUT

    @SCRIPT_TIMEOUT.setter
    def SCRIPT_TIMEOUT(self, value):
        self.__SCRIPT_TIMEOUT = value
        self.__driver.set_script_timeout(value or 0)

    @property
    def WAIT_TIMEOUT(self):
        return self.__WAIT_TIMEOUT

    @WAIT_TIMEOUT.setter
    def WAIT_TIMEOUT(self, value):
        self.__WAIT_TIMEOUT = value
        self.__driver.implicitly_wait(value or 0)

    @property
    def WINDOW_SIZE(self):
        return self.__WINDOW_SIZE

    @WINDOW_SIZE.setter
    def WINDOW_SIZE(self, value):
        if value:
            self.__WINDOW_SIZE = value
            self.__driver.set_window_size(
                *self.WINDOW_SIZE
            )

    @property
    def MAXIMIZE_WINDOW(self):
        return self.__MAXIMIZE_WINDOW

    @MAXIMIZE_WINDOW.setter
    def MAXIMIZE_WINDOW(self, value):
        if value and not self.__WINDOW_SIZE:
            self.__MAXIMIZE_WINDOW = value
            self.__driver.maximize_window()
