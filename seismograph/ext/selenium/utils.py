# -*- coding: utf-8 -*-

import time
from random import randint
from functools import wraps

from ...utils import pyv
from .exceptions import ReRaiseException


def re_raise_exc(callback=None, exc_cls=ReRaiseException, message=None):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except BaseException as e:
                orig_message = pyv.get_exc_message(e)

                if message:
                    new_message = u'{}{}'.format(
                        message, u' (from {}: {})'.format(e.__class__.__name__, orig_message)
                        if orig_message else
                        '(from {})'.format(e.__class__.__name__)
                    )
                else:
                    new_message = orig_message

                raise exc_cls(new_message)

        return wrapped

    if callable(callback):
        return wrapper(callback)

    return wrapper


def random_file_name(file_ex=None):
    file_ex = file_ex or ''
    file_name = str(
        int(time.time() + randint(0, 1000)),
    )
    file_name += file_ex
    return file_name


def change_name_from_python_to_html(name):
    name = name.replace('_', '-')
    if name.startswith('-'):
        return name[1:]
    if name.endswith('-'):
        return name[:-1]
    return name


def is_ready_state_complete(browser):
    state = browser.execute_script(
        'return document.readyState',
    )
    return state == 'complete'
