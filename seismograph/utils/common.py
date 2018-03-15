# -*- coding: utf-8 -*-

import os
import sys
import time
from . import pyv

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


def pythonpaths(*paths):
    def wrapper(f):
        for path in paths:
            if path not in sys.path:
                sys.path.append(path)
        return f
    return wrapper


def get_dict_from_list(lst, **kwargs):
    """
    Get dictionary by equal filters from kwargs

    Example:

        lst = [
            {
                'name': 'hello',
            },
            {
                'name': 'world',
            }
        ]

        dct = get_dict_from_list(lst, name='hello')
    """
    if kwargs and isinstance(lst, (list, tuple)):
        for item in lst:
            comparison = all(
                item.get(k) == v
                if isinstance(v, (int, pyv.basestring))
                else
                True
                for k, v in kwargs.items()
            )
            if comparison:
                return item
        else:
            raise LookupError(
                'Dictionary from list is not found by filters: {}'.format(kwargs),
            )

    return lst


def reduce_dict(d1, d2):
    """
    Leads dictionaries to the same species.
    The standard dictionary is d2.
    """
    def prepare_lists(l1, l2):
        assert len(l1) == len(l2)

        for i in l1:
            if isinstance(i, dict):
                l1[l1.index(i)] = reduce_dict(i, l2[l1.index(i)])

        l1.sort()
        l2.sort()

    return dict(
        (
            k,
            reduce_dict(v, d2[k])
            if isinstance(v, dict) and isinstance(d2[k], dict)
            else
            prepare_lists(v, d2[k]) or v
            if isinstance(v, list) and isinstance(d2[k], list)
            else
            v,
        )
        for k, v in d1.items()
        if k in d2
    )


def reduce_list(l1, l2):
    """
    Do return new lists. l2 is standard list.
    Equal length of lists is important.
    """
    assert len(l1) == len(l2), 'Length of lists is not equal: {} != {}'.format(len(l1), len(l2))

    lst = []

    for i in l1:
        v1 = i
        v2 = l2[l1.index(i)]

        if isinstance(v1, dict):
            lst.append(reduce_dict(v1, v2))
        elif isinstance(v1, (list, tuple)):
            lst.append(reduce_list(v1, v2))
        else:
            lst.append(v1)

    lst.sort()
    l2.sort()

    return lst, list(l2)


def which(name):
    for location in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(location, name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None
