# -*- coding: utf-8 -*-

import os
import json
import logging
from functools import wraps

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from ... import case
from ... import steps
from . import drivers
from ... import suite
from ... import reason
from ... import runnable
from ...utils import pyv
from .proxy import WebDriverProxy
from .utils import random_file_name
from .polling import POLLING_EXCEPTIONS
from ...utils.common import waiting_for
from .exceptions import SeleniumExError


logger = logging.getLogger(__name__)


EX_NAME = 'selenium'

GET_DRIVER_TIMEOUT = 10
DEFAULT_POLLING_TIMEOUT = 10
DEFAULt_POLLING_DELAY = None
DEFAULT_MAXIMIZE_WINDOW = True
DEFAULT_BROWSER = drivers.FIREFOX

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
    browser = WebDriverProxy(
        driver,
        config=BrowserConfig(selenium, driver),
    )
    browser.reason_storage['browser name'] = selenium.browser_name
    return browser


def save_logs(case, selenium):
    log_file_name = lambda log_type: '{}-{}({}:{}).log'.format(
        selenium.browser_name,
        log_type,
        runnable.class_name(case),
        runnable.method_name(case),
    )

    def log_to_string(log):
        def create_string_from_item(item, tab=0, break_line=False):
            if isinstance(item, pyv.basestring):
                try:
                    item = json.loads(item)
                except BaseException:
                    pass

            if isinstance(item, dict):
                return ('\n' if break_line else '') + u'\n'.join(
                    u'{}{}: {}'.format(
                        ('  ' * tab), k, create_string_from_item(v, tab=(tab + 1), break_line=True)
                    ) for k, v in item.items()
                )
            elif isinstance(item, (list, tuple)):
                return ('\n' if break_line else '') + u'\n'.join(
                    u'{}{}'.format(
                        ('  ' * tab), create_string_from_item(i, tab=(tab + 1), break_line=True),
                    ) for i in item
                )
            else:
                item = pyv.unicode_string(item)

            return item.strip()

        string = create_string_from_item(log).strip()

        if pyv.IS_PYTHON_2:
            return string.encode('utf-8')
        return string

    with selenium.browser.disable_polling():
        for log_type in selenium.browser.log_types:
            log = selenium.browser.get_log(log_type)
            if not log:
                continue

            log_file_path = os.path.join(
                selenium.browser.config.LOGS_PATH,
                log_file_name(log_type),
            )

            try:
                with open(log_file_path, 'w') as f:
                    f.write(log_to_string(log))
            except BaseException as error:
                logger.error(error, exc_info=True)


class BrowserConfig(object):

    def __init__(self, selenium, browser):
        self.__browser = browser

        self.LOGS_PATH = selenium.config.get('LOGS_PATH')
        self.PROJECT_URL = selenium.config.get('PROJECT_URL')

        self.POLLING_DELAY = selenium.config.get(
            'POLLING_DELAY', DEFAULt_POLLING_DELAY,
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
        if self.__browser is None:
            return

        with self.__browser.disable_polling():
            self.__browser.quit()

        self.__browser = None

    def remote(self, driver_name):
        driver_name = driver_name.lower()
        remote_config = self.__config.get('REMOTE')

        if not remote_config:
            raise SeleniumExError('settings of remote not found in config')

        logger.debug(
            'Remote config: {}'.format(str(remote_config)),
        )

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

        logger.debug(
            'Ie config: {}'.format(str(ie_config)),
        )

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

        logger.debug(
            'Chrome config: {}'.format(str(chrome_config)),
        )

        driver = drivers.ChromeWebDriver(**chrome_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def firefox(self):
        firefox_config = self.__config.get('FIREFOX', {})

        logger.debug(
            'Firefox config: {}'.format(str(firefox_config)),
        )

        driver = drivers.FirefoxWebDriver(**firefox_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def phantomjs(self):
        phantom_config = self.__config.get('PHANTOMJS')

        if not phantom_config:
            raise SeleniumExError('settings of phantom js not found in config')

        logger.debug(
            'PhantomJS config: {}'.format(str(phantom_config)),
        )

        driver = drivers.PhantomJSWebDriver(**phantom_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def opera(self):
        opera_config = self.__config.get('OPERA')

        if not opera_config:
            raise SeleniumExError('settings of opera browser not found in config')

        logger.debug(
            'Opera config: {}'.format(str(opera_config)),
        )

        driver = drivers.OperaWebDriver(**opera_config)
        self.__browser = create_browser(self, driver)

        return self.__browser

    def get_browser(self, browser_name=None, timeout=None, delay=None):
        if self.__browser:
            return self.__browser

        self.__browser_name = (
            browser_name or self.__config.get('DEFAULT_BROWSER', DEFAULT_BROWSER)
        ).lower()

        def get_browser(func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except POLLING_EXCEPTIONS:
                return None

        def get_local_browser(browser_name):
            method = getattr(self, browser_name, None)

            if method:
                return method()

            raise SeleniumExError(
                'Incorrect browser name "{}"'.format(browser_name),
            )

        delay = delay or self.__config.get('POLLING_DELAY')
        timeout = timeout or self.__config.get('POLLING_TIMEOUT') or GET_DRIVER_TIMEOUT

        if self.__config.get('USE_REMOTE', False):
            driver = waiting_for(
                lambda: get_browser(self.remote, self.__browser_name),
                delay=delay,
                timeout=timeout,
                exc_cls=SeleniumExError,
                message='Browser "{}" have not been started for "{}" sec.'.format(
                    self.__browser_name, timeout,
                ),
            )
        else:
            driver = waiting_for(
                lambda: get_browser(get_local_browser, self.__browser_name),
                delay=delay,
                timeout=timeout,
                exc_cls=SeleniumExError,
                message='Browser "{}" have not been started for "{}" sec.'.format(
                    self.__browser_name, timeout,
                ),
            )

        return driver


class SeleniumAssertion(case.AssertionBase):

    DEFAULT_TIMEOUT = 0.5

    def any_text_in_page(self, browser, texts, msg=None):
        page_text = browser.text
        error_message = u'Not of those texts was not found on page "{}". Texts: [{}]'

        for text in texts:
            if text in page_text:
                break
        else:
            error_message = error_message.format(
                browser.driver.current_url,
                u', '.join(texts),
            )
            self.fail(msg or error_message)

    def text_in_page(self, browser, text_or_texts, timeout=None, msg=None):
        error_message = u'Text "{}" not found on page "{}"'

        def check_text(txt):
            try:
                return txt in browser.text
            except (HTTPException, StaleElementReferenceException):
                return False

        if isinstance(text_or_texts, (list, tuple)):
            for t in text_or_texts:
                waiting_for(
                    check_text,
                    args=(t,),
                    exc_cls=AssertionError,
                    message=msg or error_message.format(
                        t, browser.driver.current_url,
                    ),
                    delay=browser.config.POLLING_DELAY,
                    timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
                )
        else:
            waiting_for(
                check_text,
                args=(text_or_texts,),
                exc_cls=AssertionError,
                message=msg or error_message.format(
                    text_or_texts, browser.driver.current_url,
                ),
                delay=browser.config.POLLING_DELAY,
                timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
            )

    def web_element_exist(self, browser, query, timeout=None, msg=None):
        waiting_for(
            lambda: browser.query.form_object(query).exist,
            exc_cls=AssertionError,
            message=msg or u'Web element was not found on page "{}"'.format(
                browser.driver.current_url,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
        )

    def web_element_not_exist(self, browser, query, timeout=None, msg=None):
        waiting_for(
            lambda: not browser.query.form_object(query).exist,
            exc_cls=AssertionError,
            message=msg or u'Web element was found on page "{}"'.format(
                browser.driver.current_url,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
        )

    def content_in_web_element_exist(self, browser, query_object, timeout=None, msg=None):
        waiting_for(
            lambda: len(browser.query.form_object(query_object).first().text) > 0,
            exc_cls=AssertionError,
            message=msg or 'Content does not exist inside element on page "{}"'.format(
                browser.driver.current_url,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT or self.DEFAULT_TIMEOUT,
        )


assertion = SeleniumAssertion()


def get_selenium_from_case(self):
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
            self, get_selenium_from_case(self).browser, *args, **kwargs
        )
    return wrapper


class SeleniumCaseLayer(case.CaseLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)

    def on_setup(self, case):
        if not case.__browsers__ and not case.config.SELENIUM_BROWSERS:
            get_selenium_from_case(case).start()

    def on_teardown(self, case):
        selenium = get_selenium_from_case(case)

        if selenium.browser.config.LOGS_PATH:
            save_logs(case, selenium)

        selenium.stop()


class SeleniumCase(case.Case):

    __browsers__ = None
    __layers__ = (SeleniumCaseLayer(), )
    __assertion_class__ = SeleniumAssertion

    def __init__(self, *args, **kwargs):
        # do it latter
        kwargs.update(use_flows=False)

        super(SeleniumCase, self).__init__(*args, **kwargs)

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
        try:
            if self.__selenium.browser:  # if browser wasn't init, that reason can't be created
                screen_url = self.__selenium.config.get('SCREEN_URL', None)
                screen_path = self.__selenium.config.get('SCREEN_PATH', None)

                if screen_path:
                    try:
                        file_name = random_file_name('.png')
                        screen_path = os.path.join(screen_path, file_name)

                        with self.__selenium.browser.disable_polling():
                            if self.__selenium.browser.get_screenshot_as_file(screen_path):
                                if screen_url:
                                    self.__selenium.browser.reason_storage['screen url'] = u'{}{}'.format(
                                        screen_url, file_name,
                                    )
                                else:
                                    self.__selenium.browser.reason_storage['screen path'] = screen_path
                    except BaseException as error:
                        logger.warn(error, exc_info=True)

                return super(SeleniumCase, self).__reason__() + reason.create_item(
                    'Selenium',
                    'info from selenium extension',
                    *(u'{}: {}'.format(k, v) for k, v in self.__selenium.browser.reason_storage.items())
                )

            return super(SeleniumCase, self).__reason__()
        except BaseException as error:
            logger.warn(error, exc_info=True)
            return super(SeleniumCase, self).__reason__()

    def __repeat__(self):
        if self.config.SELENIUM_BROWSERS:
            for browser_name in self.config.SELENIUM_BROWSERS:
                if self.__browsers__ and browser_name not in self.__browsers__:
                    continue
                if self.__selenium.browser and self.__selenium.browser.config.LOGS_PATH:
                    save_logs(self, self.__selenium)

                self.__selenium.stop()
                self.__selenium.start(browser_name)
                yield
        elif self.__browsers__:
            for browser_name in self.__browsers__:
                if self.__selenium.browser and self.__selenium.browser.config.LOGS_PATH:
                    save_logs(self, self.__selenium)

                self.__selenium.stop()
                self.__selenium.start(browser_name)
                yield
        else:
            yield


class SeleniumSuiteLayer(suite.SuiteLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)


class SeleniumSuite(suite.Suite):

    __case_class__ = SeleniumCase
    __layers__ = (SeleniumSuiteLayer(), )
