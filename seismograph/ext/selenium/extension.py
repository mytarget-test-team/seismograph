# -*- coding: utf-8 -*-

import logging

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from . import drivers
from . import browser
from .polling import POLLING_EXCEPTIONS
from ...utils.common import waiting_for
from .exceptions import SeleniumExError


logger = logging.getLogger(__name__)


EX_NAME = 'selenium'

GET_DRIVER_TIMEOUT = 10

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
        self.__browser = browser.create(self, driver)

        return self.__browser

    def ie(self):
        ie_config = self.__config.get('IE')

        if not ie_config:
            raise SeleniumExError('settings of ie browser not found in config')

        logger.debug(
            'Ie config: {}'.format(str(ie_config)),
        )

        driver = drivers.IeWebDriver(**ie_config)
        self.__browser = browser.create(self, driver)

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
        self.__browser = browser.create(self, driver)

        return self.__browser

    def firefox(self):
        firefox_config = self.__config.get('FIREFOX', {})

        logger.debug(
            'Firefox config: {}'.format(str(firefox_config)),
        )

        driver = drivers.FirefoxWebDriver(**firefox_config)
        self.__browser = browser.create(self, driver)

        return self.__browser

    def phantomjs(self):
        phantom_config = self.__config.get('PHANTOMJS')

        if not phantom_config:
            raise SeleniumExError('settings of phantom js not found in config')

        logger.debug(
            'PhantomJS config: {}'.format(str(phantom_config)),
        )

        driver = drivers.PhantomJSWebDriver(**phantom_config)
        self.__browser = browser.create(self, driver)

        return self.__browser

    def opera(self):
        opera_config = self.__config.get('OPERA')

        if not opera_config:
            raise SeleniumExError('settings of opera browser not found in config')

        logger.debug(
            'Opera config: {}'.format(str(opera_config)),
        )

        driver = drivers.OperaWebDriver(**opera_config)
        self.__browser = browser.create(self, driver)

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
