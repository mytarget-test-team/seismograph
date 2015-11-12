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
from .exceptions import SeleniumExError


logger = logging.getLogger(__name__)


POLLING_EXCEPTIONS = (
    IOError,
    OSError,
    HTTPException,
    WebDriverException,
)
DEFAULT_POLLING_TIMEOUT = 30


def do(callback=None, timeout=DEFAULT_POLLING_TIMEOUT, delay=None):
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
                except socket.error as error:  # if connection will be refused,
                    # that we not need to continue polling
                    raise error
                except POLLING_EXCEPTIONS as error:
                    exc = error
                    if delay:
                        time.sleep(delay)
                    continue
            else:
                if exc:
                    raise exc
                raise SeleniumExError(
                    'Timeout {} exceeded'.format(timeout),
                )

        return wrapped

    if callback is not None:
        return wrapper(callback)

    return wrapper
