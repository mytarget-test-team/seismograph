# -*- coding: utf-8 -*-

import time

from ..exceptions import TimeoutException


def waiting_for(func, timeout=None, exc_cls=None, message=None, delay=None, args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or dict()

    timeout = timeout or 0
    message = message or 'Timeout "{}" exceeded'.format(timeout)

    if timeout:
        t_start = time.time()

        while time.time() <= t_start + timeout:
            result = func(*args, **kwargs)

            if result:
                return result

            if delay:
                time.sleep(delay)
        else:
            if exc_cls:
                raise exc_cls(message)
            raise TimeoutException(message)

    result = func(*args, **kwargs)

    if result:
        return result
    if exc_cls:
        raise exc_cls(message)
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
