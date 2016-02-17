# -*- coding: utf-8 -*-

from contextlib import contextmanager

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


@contextmanager
def change_config(browser,
                  wait_timeout=None,
                  polling_delay=None,
                  polling_timeout=None,
                  page_load_timeout=None):
    to_restore = {}

    if wait_timeout:
        to_restore['wait_timeout'] = browser.config.WAIT_TIMEOUT
        browser.config.WAIT_TIMEOUT = wait_timeout

    if polling_delay:
        to_restore['polling_delay'] = browser.config.POLLING_DELAY
        browser.config.POLLING_DELAY = polling_delay

    if polling_timeout:
        to_restore['polling_timeout'] = browser.config.POLLING_TIMEOUT
        browser.config.POLLING_TIMEOUT = polling_timeout

    if page_load_timeout:
        to_restore['page_load_timeout'] = browser.config.PAGE_LOAD_TIMEOUT
        browser.config.PAGE_LOAD_TIMEOUT = page_load_timeout

    try:
        yield
    finally:
        if 'wait_timeout' in to_restore:
            browser.config.WAIT_TIMEOUT = to_restore['wait_timeout']

        if 'polling_delay' in to_restore:
            browser.config.POLLING_DELAY = to_restore['polling_delay']

        if 'polling_timeout' in to_restore:
            browser.config.POLLING_TIMEOUT = to_restore['polling_timeout']

        if 'page_load_timeout' in to_restore:
            browser.config.PAGE_LOAD_TIMEOUT = to_restore['page_load_timeout']


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
        if value is not None:
            self.__PAGE_LOAD_TIMEOUT = value
            self.__driver.set_page_load_timeout(value)

    @property
    def SCRIPT_TIMEOUT(self):
        return self.__SCRIPT_TIMEOUT

    @SCRIPT_TIMEOUT.setter
    def SCRIPT_TIMEOUT(self, value):
        if value is not None:
            self.__SCRIPT_TIMEOUT = value
            self.__driver.set_script_timeout(value)

    @property
    def WAIT_TIMEOUT(self):
        return self.__WAIT_TIMEOUT

    @WAIT_TIMEOUT.setter
    def WAIT_TIMEOUT(self, value):
        if value is not None:
            self.__WAIT_TIMEOUT = value
            self.__driver.implicitly_wait(value)

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
