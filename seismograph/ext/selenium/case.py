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

from ... import case
from ... import steps
from ... import reason
from ... import runnable
from ...utils import pyv
from .extension import EX_NAME
from .utils import random_file_name
from ...utils.common import waiting_for


logger = logging.getLogger(__name__)


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


def get_selenium_from_case(self):
    return self._SeleniumCase__selenium


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
