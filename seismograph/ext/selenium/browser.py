# -*- coding: utf-8 -*-

from .proxy import WebDriverProxy


DEFAULT_POLLING_TIMEOUT = 10
DEFAULT_POLLING_DELAY = None
DEFAULT_MAXIMIZE_WINDOW = True


def create(selenium, driver):
    browser = WebDriverProxy(
        driver,
        config=BrowserConfig(selenium, driver),
    )
    browser.reason_storage['browser name'] = selenium.browser_name
    return browser


class BrowserConfig(object):

    def __init__(self, selenium, browser):
        self.__browser = browser

        self.LOGS_PATH = selenium.config.get('LOGS_PATH')
        self.PROJECT_URL = selenium.config.get('PROJECT_URL')

        self.POLLING_DELAY = selenium.config.get(
            'POLLING_DELAY', DEFAULT_POLLING_DELAY,
        )
        self.POLLING_TIMEOUT = selenium.config.get(
            'POLLING_TIMEOUT', DEFAULT_POLLING_TIMEOUT,
        )

        self.__SCRIPT_TIMEOUT = None
        self.SCRIPT_TIMEOUT = selenium.config.get('SCRIPT_TIMEOUT')

        self.__IMPLICITLY_WAIT = None
        self.IMPLICITLY_WAIT = selenium.config.get('IMPLICITLY_WAIT')

        self.__WINDOW_SIZE = None
        self.WINDOW_SIZE = selenium.config.get('WINDOW_SIZE')

        self.__MAXIMIZE_WINDOW = False
        self.MAXIMIZE_WINDOW = selenium.config.get(
            'MAXIMIZE_WINDOW', DEFAULT_MAXIMIZE_WINDOW,
        )

    @property
    def SCRIPT_TIMEOUT(self):
        return self.__SCRIPT_TIMEOUT

    @SCRIPT_TIMEOUT.setter
    def SCRIPT_TIMEOUT(self, value):
        if value is not None:
            self.__SCRIPT_TIMEOUT = value
            self.__browser.set_script_timeout(value)

    @property
    def IMPLICITLY_WAIT(self):
        return self.__IMPLICITLY_WAIT

    @IMPLICITLY_WAIT.setter
    def IMPLICITLY_WAIT(self, value):
        if value is not None:
            self.__IMPLICITLY_WAIT = value
            self.__browser.implicitly_wait(value)

    @property
    def WINDOW_SIZE(self):
        return self.__WINDOW_SIZE

    @WINDOW_SIZE.setter
    def WINDOW_SIZE(self, value):
        if value:
            self.__WINDOW_SIZE = value
            self.__browser.set_window_size(
                *self.WINDOW_SIZE
            )

    @property
    def MAXIMIZE_WINDOW(self):
        return self.__MAXIMIZE_WINDOW

    @MAXIMIZE_WINDOW.setter
    def MAXIMIZE_WINDOW(self, value):
        if value and not self.__WINDOW_SIZE:
            self.__MAXIMIZE_WINDOW = value
            self.__browser.maximize_window()
