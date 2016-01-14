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
DEFAULT_GET_BROWSER_DELAY = 0.5
DEFAULT_GET_BROWSER_TIMEOUT = 10
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
        self.__is_running = False
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

    @property
    def is_running(self):
        return self.__is_running

    def start(self, browser_name=None, timeout=None, delay=None):
        if not self.__is_running:
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

            delay = delay or self.__config.get(
                'POLLING_DELAY', DEFAULT_GET_BROWSER_DELAY,
            )
            timeout = timeout or self.__config.get(
                'POLLING_TIMEOUT', DEFAULT_GET_BROWSER_TIMEOUT,
            )
            args = {
                True: (self.remote, self.__browser_name),
                False: (get_local_browser, self.__browser_name),
            }

            self.__browser = waiting_for(
                get_browser,
                delay=delay,
                timeout=timeout,
                exc_cls=SeleniumExError,
                args=args[bool(self.__config.get('USE_REMOTE', False))],
                message='Browser "{}" has not been started for "{}" sec.'.format(
                    self.__browser_name, timeout,
                ),
            )

            self.__is_running = True

    def stop(self):
        if self.__is_running:
            with self.__browser.disable_polling():
                self.__browser.close()
                self.__browser.quit()
            self.__is_running = False

    def remote(self, driver_name):
        driver_name = driver_name.lower()
        remote_config = self.__config.get('REMOTE')

        if not remote_config:
            raise SeleniumExError(
                'settings for remote is not found in config',
            )

        logger.debug(
            'Remote config: {}'.format(str(remote_config)),
        )

        if not remote_config.get('desired_capabilities'):
            capabilities = get_capabilities(driver_name)
            capabilities.update(
                remote_config.pop('capabilities', {}).get(driver_name, {}),
            )
            remote_config['desired_capabilities'] = capabilities

        driver = drivers.RemoteWebDriver(**remote_config)
        return browser.create(self, driver)

    def ie(self):
        ie_config = self.__config.get('IE')

        if not ie_config:
            raise SeleniumExError(
                'settings for ie browser is not found in config',
            )

        logger.debug(
            'Ie config: {}'.format(str(ie_config)),
        )

        driver = drivers.IeWebDriver(**ie_config)
        return browser.create(self, driver)

    def chrome(self):
        """
        :rtype: selenium.webdriver.chrome.webdriver.WebDriver
        """
        chrome_config = self.__config.get('CHROME')

        if not chrome_config:
            raise SeleniumExError(
                'settings for chrome browser is not found in config',
            )

        logger.debug(
            'Chrome config: {}'.format(str(chrome_config)),
        )

        driver = drivers.ChromeWebDriver(**chrome_config)
        return browser.create(self, driver)

    def firefox(self):
        firefox_config = self.__config.get('FIREFOX', {})

        logger.debug(
            'Firefox config: {}'.format(str(firefox_config)),
        )

        driver = drivers.FirefoxWebDriver(**firefox_config)
        return browser.create(self, driver)

    def phantomjs(self):
        phantom_config = self.__config.get('PHANTOMJS')

        if not phantom_config:
            raise SeleniumExError(
                'settings for phantom js is not found in config',
            )

        logger.debug(
            'PhantomJS config: {}'.format(str(phantom_config)),
        )

        driver = drivers.PhantomJSWebDriver(**phantom_config)
        return browser.create(self, driver)

    def opera(self):
        opera_config = self.__config.get('OPERA')

        if not opera_config:
            raise SeleniumExError(
                'settings for opera browser is not found in config',
            )

        logger.debug(
            'Opera config: {}'.format(str(opera_config)),
        )

        driver = drivers.OperaWebDriver(**opera_config)
        return browser.create(self, driver)
