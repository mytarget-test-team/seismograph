# -*- coding: utf-8 -*-

import sys
import time
from contextlib import contextmanager

from ..exceptions import TimeoutException


WAITING_FOR_TIMEOUT = 30


def waiting_for(func, timeout=None, exc=None, message=None, sleep=None, args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or {}

    timeout = timeout or WAITING_FOR_TIMEOUT

    t_start = time.time()

    while time.time() <= t_start + timeout:
        result = func(*args, **kwargs)

        if result:
            return result

        if sleep:
            time.sleep(sleep)
    else:
        message = message or 'Timeout {} exceeded'.format(timeout)
        if exc:
            raise exc(message)
        raise TimeoutException(message)


def call_to_chain(chain, method_name, *args, **kwargs):
    for obj in chain:
        if method_name:
            getattr(obj, method_name)(*args, **kwargs)
        else:
            obj(*args, **kwargs)


def measure_time():
    start_time = time.time()
    return lambda: time.time() - start_time


@contextmanager
def dev_null():
    class MockStd(object):

        def __getattr__(self, item):
            def null(*args, **kwargs):
                pass
            return null

    stdout = sys.stdout
    sys.stdout = MockStd()
    try:
        yield
    finally:
        sys.stdout = stdout


class MPSupportedValue(object):

    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        if hasattr(self._value, 'value'):
            return self._value.value
        return self._value

    @value.setter
    def value(self, value):
        if hasattr(self._value, 'value'):
            self._value.value = value
        else:
            self._value = value

    def set_mp(self, value):
        self._value = value
