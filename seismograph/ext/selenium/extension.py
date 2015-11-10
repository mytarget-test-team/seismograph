# -*- coding: utf-8 -*-

import os
import logging
from functools import wraps

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from ... import case
from ... import steps
from . import drivers
from ... import suite
from ... import runnable
from .proxy import WebDriverProxy
from ...tools import create_reason
from .utils import random_file_name
from ...utils.common import waiting_for
from .exceptions import SeleniumExError
from ...exceptions import TimeoutException


logger = logging.getLogger(__name__)


EX_NAME = 'selenium'

GET_DRIVER_TIMEOUT = 10

DEFAULT_WINDOW_SIZE = None
DEFAULT_POLLING_TIMEOUT = 30
DEFAULT_MAXIMIZE_WINDOW = True
DEFAULT_DRIVER = drivers.CHROME

DRIVER_TO_CAPABILITIES = {
    drivers.OPERA: DesiredCapabilities.OPERA,
    drivers.CHROME: DesiredCapabilities.CHROME,
    drivers.FIREFOX: DesiredCapabilities.FIREFOX,
    drivers.PHANTOMJS: DesiredCapabilities.PHANTOMJS,
    drivers.IE: DesiredCapabilities.INTERNETEXPLORER,
}


def get_capabilities(driver_name):
    """
    Get capabilities of driver

    :param driver_name: driver name
    :type driver_name: str
    """
    try:
        return DRIVER_TO_CAPABILITIES[driver_name]
    except KeyError:
        raise SeleniumExError(
            'Capabilities for driver "{}" is not found'.find(driver_name),
        )


def create_browser(selenium, driver):
    return WebDriverProxy(
        driver,
        config=BrowserConfig(selenium, driver),
    )


class BrowserConfig(object):

    def __init__(self, selenium, browser):
        self.__browser = browser

        self.__WINDOW_SIZE = None
        self.WINDOW_SIZE = selenium.config.get('WINDOW_SIZE')

        self.__MAXIMIZE_WINDOW = False
        self.MAXIMIZE_WINDOW = selenium.config.get('MAXIMIZE_WINDOW')

        self.PROJECT_URL = selenium.config.get('PROJECT_URL')
        self.POLLING_TIMEOUT = selenium.config.get('POLLING_TIMEOUT')

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


class Selenium(object):

    def __init__(self, config):
        self.__config = config

        self.__browser = None
        self.__browser_name = None

    def __enter__(self):
        self.start()
        return self.__browser

    def __exit__(self, *args, **kwargs):
        self.stop()

    @property
    def config(self):
        return self.__config

    @property
    def browser(self):
        return self.__browser

    @property
    def browser_name(self):
        return self.__browser_name

    def start(self, *args, **kwargs):
        if self.__browser:
            return

        self.get_browser(*args, **kwargs)

    def stop(self):
        if not self.__browser:
            return

        self.__browser.quit()
        self.__browser = None

    def remote(self, driver_name):
        remote_config = self.__config.get('REMOTE')

        if not remote_config:
            raise SeleniumExError('settings of remote not found in config')

        logger.debug('Remote config: {}'.format(str(remote_config)))

        options = remote_config.get('OPTIONS', {})
        capabilities = get_capabilities(driver_name)
        capabilities.update(
            remote_config['CAPABILITIES'][driver_name],
        )

        driver = drivers.RemoteWebDriver(
            desired_capabilities=capabilities,
            **options
        )
        self.__browser = create_browser(self, driver)

        return self.__browser

    def ie(self):
        ie_config = self.__config.get('IE')

        if not ie_config:
            raise SeleniumExError('settings of ie browser not found in config')

        logger.debug('Ie config: {}'.format(str(ie_config)))

        driver = drivers.IeWebDriver(**ie_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def chrome(self):
        """
        :rtype: selenium.webdriver.chrome.webdriver.WebDriver
        """
        chrome_config = self.__config.get('CHROME')

        if not chrome_config:
            raise SeleniumExError('settings of chrome browser not found in config')

        logger.debug('Chrome config: {}'.format(str(chrome_config)))

        driver = drivers.ChromeWebDriver(**chrome_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def firefox(self):
        firefox_config = self.__config.get('FIREFOX', {})

        logger.debug('Firefox config: {}'.format(str(firefox_config)))

        driver = drivers.FirefoxWebDriver(**firefox_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def phantomjs(self):
        phantom_config = self.__config.get('PHANTOMJS')

        if not phantom_config:
            raise SeleniumExError('settings of phantom js not found in config')

        logger.debug('PhantomJS config: {}'.format(str(phantom_config)))

        driver = drivers.PhantomJSWebDriver(**phantom_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def opera(self):
        opera_config = self.__config.get('OPERA')

        if not opera_config:
            raise SeleniumExError('settings of opera browser not found in config')

        logger.debug('Opera config: {}'.format(str(opera_config)))

        driver = drivers.OperaWebDriver(**opera_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def _get_local_driver(self, driver_name):
        method = getattr(self, driver_name, None)

        if method:
            return method()

        raise SeleniumExError(
            'Incorrect browser name "{}"'.format(driver_name),
        )

    def get_browser(self, browser_name=None, timeout=None):
        if self.__browser:
            return self.__browser

        self.__browser_name = (
            browser_name or self.__config.get('DEFAULT_BROWSER', drivers.FIREFOX)
        ).lower()

        def get_browser(func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (IOError, OSError, HTTPException, WebDriverException):
                return None

        if self.__config.get('USE_REMOTE', False):
            driver = waiting_for(
                lambda: get_browser(self.remote, self.__browser_name),
                timeout=timeout or GET_DRIVER_TIMEOUT,
            )
        else:
            driver = waiting_for(
                lambda: get_browser(self._get_local_driver, self.__browser_name),
                timeout=timeout or GET_DRIVER_TIMEOUT,
            )

        return driver


class SeleniumAssertion(case.AssertionBase):

    DEFAULT_TIMEOUT = 3

    def one_of_texts_in_page(self, browser, texts, msg=None):
        page_text = browser.text
        error_message = u'Not of those texts was not found in page "{}". Texts: [{}]'

        for text in texts:
            if text in page_text:
                break
        else:
            error_message = error_message.format(
                browser.current_url,
                u', '.join(texts),
            )
            self.fail(msg or error_message)

    def text_in_page(self, browser, text_or_texts, timeout=None, msg=None):
        error_message = u'Text "{}" not found in page "{}"'

        def check_text(txt):
            try:
                return txt in browser.text
            except (HTTPException, StaleElementReferenceException):
                return False

        if isinstance(text_or_texts, (list, tuple)):
            for t in text_or_texts:
                try:
                    waiting_for(
                        check_text,
                        timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
                        args=(t,),
                    )
                except TimeoutException:
                    self.fail(
                        msg or error_message.format(
                            t, browser.current_url,
                        ),
                    )
        else:
            try:
                waiting_for(
                    check_text,
                    timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
                    args=(text_or_texts,),
                )
            except TimeoutException:
                self.fail(
                    msg or error_message.format(
                        text_or_texts, browser.current_url,
                    ),
                )

    def web_element_exist(self, browser, query_object, timeout=None, msg=None):
        try:
            waiting_for(
                lambda: browser.query.form_object(query_object).exist,
                timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
            )
        except TimeoutException:
            self.fail(msg or u'Web element was not found')

    def web_element_not_exist(self, browser, query_object, timeout=None, msg=None):
        try:
            waiting_for(
                lambda: not browser.query.form_object(query_object).exist,
                timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
            )
        except TimeoutException:
            self.fail(msg or u'Web element was found')

    def content_in_web_element_exist(self, browser, query_object, timeout=None, msg=None):
        try:
            waiting_for(
                lambda: len(browser.query.form_object(query_object).first().text) > 0,
                timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
            )
        except TimeoutException:
            self.true(msg or 'Content does not exist in element')


assertion = SeleniumAssertion()


def _get_selenium_from_case(self):
    return self._SeleniumCase__selenium


def case_of_browsers(*browsers):
    def wrapper(cls):
        setattr(cls, '__browsers__', browsers)
        return cls
    return wrapper


def inject_driver(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        return f(
            self, _get_selenium_from_case(self).browser, *args, **kwargs
        )
    return wrapper


class SeleniumCaseLayer(case.CaseLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)

    def on_setup(self, case):
        if not case.__browsers__:
            _get_selenium_from_case(case).start()

    def on_teardown(self, case):
        if not case.__browsers__:
            _get_selenium_from_case(case).stop()


class SeleniumCase(case.Case):

    __browsers__ = None
    __create_reason__ = True
    __layers__ = (SeleniumCaseLayer(), )
    __assertion_class__ = SeleniumAssertion

    def __init__(self, *args, **kwargs):
        # do it latter
        kwargs.update(use_flows=False)

        super(SeleniumCase, self).__init__(*args, **kwargs)

        if self.config.SELENIUM_BROWSERS:
            self.__browsers__ = self.config.SELENIUM_BROWSERS

        self.__selenium = self.ext('selenium')

        if steps.is_step_by_step_case(self):
            step_methods = []

            for step_method in steps.get_step_methods(self):
                step_methods.append(inject_driver(step_method))

            setattr(self.__class__, steps.STEPS_STORAGE_ATTRIBUTE_NAME, step_methods)
        else:
            method = getattr(self.__class__, runnable.method_name(self))
            setattr(self.__class__, runnable.method_name(self), inject_driver(method))

            case.apply_flows(self)

    def __reason__(self):
        reason_args = []

        for k, v in self.__selenium.browser.reason_storage.items():
            reason_args.append('{}: {}'.format(k, v))

        screen_url = self.__selenium.config.get('SCREEN_URL', None)
        screen_path = self.__selenium.config.get('SCREEN_PATH', None)

        if screen_path:
            file_name = random_file_name('.png')
            screen_path = os.path.join(screen_path, file_name)

            self.__selenium.browser.save_screenshot(screen_path)

            if screen_url:
                reason_args.append(
                    u'screen url: {}{}'.format(screen_url, file_name),
                )
            else:
                reason_args.append('screen path: {}'.format(screen_path))

        return create_reason(
            'Selenium',
            'info from selenium extension',
            'browser name: {}'.format(self.__selenium.browser_name),
            *reason_args
        )

    def __repeat__(self):
        if self.__browsers__:
            for browser_name in self.__browsers__:
                self.__selenium.start(browser_name)
                try:
                    yield
                finally:
                    self.__selenium.stop()
        else:
            yield


class SeleniumSuiteLayer(suite.SuiteLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)


class SeleniumSuite(suite.Suite):

    __case_class__ = SeleniumCase
    __layers__ = (SeleniumSuiteLayer(), )
