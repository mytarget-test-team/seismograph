# -*- coding: utf-8 -*-

import os
import logging
from functools import wraps
from pprint import PrettyPrinter

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException

from ... import case
from ... import steps
from ... import reason
from ... import runnable
from .query import QueryResult
from .extension import EX_NAME
from .utils import random_file_name
from ...utils.common import waiting_for


logger = logging.getLogger(__name__)


def make_with_browsers(*browsers):
    def wrapper(cls):
        setattr(cls, '__browsers__', browsers)
        return cls
    return wrapper


def require_browser(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        selenium = self.ext(EX_NAME)
        return f(
            self, selenium.browser, *args, **kwargs
        )
    return wrapper


def make_setup(case, browser_name=None):
    selenium = case.ext(EX_NAME)
    selenium.start(browser_name)

    if case.__page_class__:
        case.checkout_page(case.__page_class__)


def save_logs(case):
    selenium = case.ext(EX_NAME)
    log_file_name = lambda log_type: '{}-{}({}:{}).log'.format(
        selenium.browser_name,
        log_type,
        runnable.class_name(case),
        runnable.method_name(case),
    )
    try:
        with selenium.browser.disable_polling():
            for log_type in selenium.browser.log_types:
                log = selenium.browser.get_log(log_type)
                if not log:
                    continue

                log_file_path = os.path.join(
                    selenium.config.get('LOGS_PATH'),
                    log_file_name(log_type),
                )

                try:
                    with open(log_file_path, 'w') as f:
                        PrettyPrinter(stream=f).pprint(log)
                except BaseException as error:
                    logger.error(error, exc_info=True)
    except WebDriverException as warn:
        logger.warn(warn, exc_info=True)
    except BaseException as error:
        logger.er(error, exc_info=True)


class SeleniumAssertion(case.AssertionBase):

    @staticmethod
    def any_text_exist(proxy, texts, msg=None, timeout=None):
        def check_exist():
            page_text = proxy.text
            for text in texts:
                if text in page_text:
                    return True
            return False

        waiting_for(
            check_exist,
            exc_cls=AssertionError,
            message=msg or u'Not of those texts was not found on page by URL "{}". Texts: [{}]'.format(
                proxy.browser.current_url,
                u', '.join(texts),
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def text_exist(proxy, text, msg=None, timeout=None):
        def check_text():
            try:
                return text in proxy.text
            except (HTTPException, StaleElementReferenceException):
                return False

        waiting_for(
            check_text,
            exc_cls=AssertionError,
            message=msg or u'Text "{}" not found on page by URL "{}"'.format(
                text, proxy.browser.current_url,
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    def texts_exist(self, proxy, texts, timeout=None, msg=None):
        for text in texts:
            self.text_exist(proxy, text, timeout=timeout, msg=msg)

    @staticmethod
    def text_not_exist(proxy, text, msg=None, timeout=None):
        def check_text():
            try:
                return text not in proxy.text
            except (HTTPException, StaleElementReferenceException):
                return False

        waiting_for(
            check_text,
            exc_cls=AssertionError,
            message=msg or u'Text "{}" was found on page by URL "{}"'.format(
                text, proxy.browser.current_url,
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    def texts_not_exist(self, proxy, texts, timeout=None, msg=None):
        for text in texts:
            self.text_not_exist(proxy, text, timeout=timeout, msg=msg)

    @staticmethod
    def web_element_exist(proxy, query, msg=None, timeout=None):
        if isinstance(query, QueryResult):
            function = lambda: query.exist
        else:
            function = lambda: query(proxy).exist

        waiting_for(
            function,
            exc_cls=AssertionError,
            message=msg or u'Web element was not found on page by URL "{}"'.format(
                proxy.browser.current_url,
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def web_element_not_exist(proxy, query, msg=None, timeout=None):
        if isinstance(query, QueryResult):
            function = lambda: not query.exist
        else:
            function = lambda: not query(proxy).exist

        waiting_for(
            function,
            exc_cls=AssertionError,
            message=msg or u'Web element was found on page by URL "{}"'.format(
                proxy.browser.current_url,
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def content_exist(proxy, query, msg=None, timeout=None):
        waiting_for(
            lambda: len(query(proxy).first().text) > 0,
            exc_cls=AssertionError,
            message=msg or 'Content is not exist inside element on page by URL "{}"'.format(
                proxy.browser.current_url,
            ),

            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def content_not_exist(proxy, query, msg=None, timeout=None):
        waiting_for(
            lambda: len(query(proxy).first().text) == 0,
            exc_cls=AssertionError,
            message=msg or 'Content is exist inside element on page by URL "{}"'.format(
                proxy.browser.current_url,
            ),
            delay=proxy.config.POLLING_DELAY,
            timeout=timeout or proxy.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def current_url_equal(browser, url, msg=None, timeout=None):
        waiting_for(
            lambda: browser.current_url == url,
            exc_cls=AssertionError,
            message=msg or '{} != {}'.format(
                browser.current_url, url,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def current_url_not_equal(browser, url, msg=None, timeout=None):
        waiting_for(
            lambda: browser.current_url != url,
            exc_cls=AssertionError,
            message=msg or '{} == {}'.format(
                browser.current_url, url,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def current_path_equal(browser, path, msg=None, timeout=None):
        waiting_for(
            lambda: browser.current_path == path,
            exc_cls=AssertionError,
            message=msg or '{} != {}'.format(
                browser.current_path, path,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def current_path_not_equal(browser, path, msg=None, timeout=None):
        waiting_for(
            lambda: browser.current_path != path,
            exc_cls=AssertionError,
            message=msg or '{} == {}'.format(
                browser.current_path, path,
            ),
            delay=browser.config.POLLING_DELAY,
            timeout=timeout or browser.config.POLLING_TIMEOUT,
        )

    @staticmethod
    def any_text_for_field_exist(field, texts, msg=None, timeout=None):
        def check_exist():
            page_text = field.group.area.text
            for txt in texts:
                if txt in page_text:
                    return True
            return False

        waiting_for(
            check_exist,
            exc_cls=AssertionError,
            message=msg or u'Text for field "{}" not found on page by URL "{}". Text list: [{}]'.format(
                field.name,
                field.group.area.browser.current_url,
                u', '.join(texts),
            ),
            delay=field.config.POLLING_DELAY,
            timeout=timeout or field.config.POLLING_TIMEOUT,
        )

    def texts_for_field_exist(self, field, texts, msg=None, timeout=None):
        for text in texts:
            self.text_for_field_exist(field, text, timeout=timeout, msg=msg)

    def text_for_field_exist(self, field, text, msg=None, timeout=None):
        error_message = msg or u'Text for field "{}" not found on page by URL "{}". Text: "{}"'.format(
            field.name,
            field.group.area.browser.current_url,
            text,
        )

        self.text_exist(
            field.group.area,
            text,
            timeout=timeout,
            msg=error_message,
        )


assertion = SeleniumAssertion()


class SeleniumCaseLayer(case.CaseLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)

    def on_teardown(self, case):
        selenium = case.ext(EX_NAME)
        logs_path = selenium.config.get('LOGS_PATH')

        if logs_path:
            save_logs(case)

        selenium.stop()


class SeleniumCase(case.Case):

    __browsers__ = None
    __page_class__ = None
    __require_browser__ = True
    __layers__ = (SeleniumCaseLayer(), )
    __assertion_class__ = SeleniumAssertion

    def __init__(self, *args, **kwargs):
        if self.__require_browser__:
            kwargs.update(use_flows=False)
    
            super(SeleniumCase, self).__init__(*args, **kwargs)

            if steps.is_step_by_step_case(self):
                step_methods = []

                for step_method in steps.get_step_methods(self):
                    step_methods.append(require_browser(step_method))

                setattr(self.__class__, steps.STEPS_STORAGE_ATTRIBUTE_NAME, step_methods)
            else:
                method = getattr(self.__class__, runnable.method_name(self))
                setattr(self.__class__, runnable.method_name(self), require_browser(method))

                case.apply_flows(self)
        else:
            super(SeleniumCase, self).__init__(*args, **kwargs)

            self.page = None

    def __reason__(self):
        selenium = self.ext(EX_NAME)
        reasons = [
            super(SeleniumCase, self).__reason__(),
        ]

        try:
            screen_url = selenium.config.get('SCREEN_URL', None)
            screen_path = selenium.config.get('SCREEN_PATH', None)

            if screen_path:
                try:
                    file_name = random_file_name('.png')
                    screen_path = os.path.join(screen_path, file_name)

                    with selenium.browser.disable_polling():
                        if selenium.browser.get_screenshot_as_file(screen_path):
                            if screen_url:
                                selenium.browser.reason_storage['screen url'] = u'{}{}'.format(
                                    screen_url, file_name,
                                )
                            else:
                                selenium.browser.reason_storage['screen path'] = screen_path
                except BaseException as error:
                    logger.warn(error, exc_info=True)

            reasons.append(
                reason.item(
                    'Selenium',
                    'info from selenium extension',
                    *(u'{}: {}'.format(k, v) for k, v in selenium.browser.reason_storage.items())
                ),
            )
        except BaseException as error:
            logger.error(error, exc_info=True)

        return reason.join(reasons)

    def __repeat__(self):
        if self.config.SELENIUM_BROWSERS and self.__repeatable__:
            for browser_name in self.config.SELENIUM_BROWSERS:
                if self.__browsers__ and browser_name not in self.__browsers__:
                    continue

                make_setup(self, browser_name)
                yield
        elif self.__browsers__ and self.__repeatable__:
            for browser_name in self.__browsers__:
                make_setup(self, browser_name)
                yield
        else:
            make_setup(self)
            yield

    def checkout_page(self, page_cls):
        self.page = page_cls(self.ext(EX_NAME).browser)
