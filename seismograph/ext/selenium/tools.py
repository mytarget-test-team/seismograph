# -*- coding: utf8 -*-

import time
from functools import wraps

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import WebDriverException

from ...utils import pyv
from ...exceptions import TimeoutException
from .exceptions import ReRaiseWebDriverException


POLLING_EXCEPTIONS = (
    IOError,
    OSError,
    HTTPException,
    WebDriverException,
)
DEFAULT_POLLING_TIMEOUT = 30


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
                orig_message = pyv.get_exc_message(e)

                if message:
                    new_message = u'{}{}'.format(
                        message, u' ({})'.format(orig_message) if orig_message else ''
                    )
                else:
                    new_message = orig_message

                raise exc_cls(new_message)

        return wrapped

    if callable(callback):
        return wrapper(callback)

    return wrapper
