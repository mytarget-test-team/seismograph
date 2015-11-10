# -*- coding: utf8 -*-

from __future__ import absolute_import

import time
from random import randint
from functools import wraps

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains as __ActionChains

from ...utils import pyv
from ...exceptions import TimeoutException
from .exceptions import ReRaiseWebDriverException
from .utils import change_name_from_python_to_html


DEFAULT_POLLING_TIMEOUT = 30
POLLING_EXCEPTIONS = (
    IOError,
    OSError,
    HTTPException,
    WebDriverException,
)


class ActionChains(__ActionChains):

    def __init__(self, proxy):
        super(ActionChains, self).__init__(proxy.driver)

    def __call__(self, proxy):
        return self.__class__(proxy)

    def reset(self):
        self._actions = []

    def perform(self, reset=True):
        super(ActionChains, self).perform()

        if reset:
            self.reset()


def create_screen_file_name():
    file_ex = '.png'
    file_name = str(
        int(time.time() + randint(0, 1000)),
    )
    file_name += file_ex
    return file_name


class WebElementToObject(object):

    def __init__(self, proxy, allow_raise=True):
        self.__dict__['__proxy__'] = proxy
        self.__dict__['__allow_raise__'] = allow_raise

    @property
    def css(self):
        return WebElementCssToObject(
            self.__dict__['__proxy__'],
        )

    def __getattr__(self, item):
        atr = self.__dict__['__proxy__'].get_attribute(
            change_name_from_python_to_html(item),
        )

        if atr:
            return atr

        if self.__dict__['__allow_raise__']:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        self.__dict__['__proxy__'].parent.execute_script(
            'arguments[0].setAttribute(arguments[1], arguments[2]);',
            self.__dict__['__proxy__'],
            change_name_from_python_to_html(key),
            value
        )


class WebElementCssToObject(object):

    def __init__(self, proxy):
        self.__dict__['__proxy__'] = proxy

    def __getattr__(self, item):
        return self.__dict__['__proxy__'].value_of_css_property(
            change_name_from_python_to_html(item),
        )

    def __setattr__(self, key, value):
        self.__dict__['__proxy__'].parent.execute_script(
            'arguments[0].style[arguments[1]] = arguments[2];',
            self.__dict__['__proxy__'],
            change_name_from_python_to_html(key),
            value
        )


def make_object(web_element, allow_raise=True):
    return WebElementToObject(web_element, allow_raise=allow_raise)


def polling(callback=None, timeout=DEFAULT_POLLING_TIMEOUT):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            exc = None
            t_start = time.time()

            while time.time() <= t_start + timeout:
                try:
                    return f(*args, **kwargs)
                except POLLING_EXCEPTIONS as error:
                    exc = error
                    continue
            else:
                if exc:
                    raise exc
                raise

        return wrapped

    if callback is not None:
        return wrapper(callback)

    return wrapper


def re_raise_wd_exc(callback=None, exc_cls=ReRaiseWebDriverException, message=None):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (TimeoutException, WebDriverException) as e:
                raise exc_cls(message or pyv.get_exc_message(e))

        return wrapped

    if callable(callback):
        return wrapper(callback)

    return wrapper
