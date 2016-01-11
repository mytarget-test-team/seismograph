# -*- coding: utf8 -*-

import time
import socket
import logging
from functools import wraps

try:
    from httplib import HTTPException
except ImportError:  # please python 3
    from http.client import HTTPException

from selenium.common.exceptions import WebDriverException

from ...utils import pyv
from .exceptions import PollingTimeoutExceeded


logger = logging.getLogger(__name__)


POLLING_EXCEPTIONS = (
    IOError,
    OSError,
    HTTPException,
    WebDriverException,
)
DEFAULT_POLLING_TIMEOUT = 30
DEFAULT_POLLING_DELAY = None


def do(callback,
       exceptions=POLLING_EXCEPTIONS,
       timeout=DEFAULT_POLLING_TIMEOUT,
       delay=DEFAULT_POLLING_DELAY):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            exc = None
            t_start = time.time()

            while time.time() <= t_start + timeout:
                try:
                    logger.debug(
                        u'Do polling, try to call "{}", args={}, kwargs={}'.format(
                            pyv.get_func_name(f), pyv.unicode(args), pyv.unicode(kwargs),
                        ),
                    )
                    return f(*args, **kwargs)
                except socket.error:  # if connection will be refused,
                    # then we not need to continue polling
                    raise
                except exceptions as error:
                    exc = error
                    if delay:
                        time.sleep(delay)
                    continue
            else:
                if exc:
                    raise
                raise PollingTimeoutExceeded(str(timeout))

        return wrapped
    return wrapper(callback)


def wrap(timeout=DEFAULT_POLLING_TIMEOUT,
         delay=DEFAULT_POLLING_DELAY,
         exceptions=POLLING_EXCEPTIONS):
    def wrapper(f):
        return do(f,
                  timeout=timeout,
                  delay=delay,
                  exceptions=exceptions)
    return wrapper
