# -*- coding: utf-8 -*-

import time
import inspect
from random import randint
from functools import wraps

from ...utils import pyv
from .exceptions import ReRaiseException


def re_raise_exc(callback=None, exc_cls=ReRaiseException, message=None):
    """
    Decorator for except any exception and reraise it.
    """
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
    """
    Generate random file name
    """
    file_ex = file_ex or ''
    file_name = str(
        int(time.time() + randint(0, 1000)),
    )
    file_name += file_ex
    return file_name


def change_name_from_python_to_html(name):
    """
    Attribute name from DOM tree has different
    format than python style.
    This function help with that problem.
    """
    name = name.replace('_', '-')
    if name.startswith('-'):
        return name[1:]
    if name.endswith('-'):
        return name[:-1]
    return name


def is_ready_state_complete(browser):
    """
    Do return True if document ready
    state is complete else False
    """
    state = browser.execute_script(
        'return document.readyState',
    )
    return state == 'complete'


def declare_standard_callback(func):
    """
    Check for signature of function which should
    has only one argument in signature and return it.
    """
    if not callable(func):
        return func

    try:
        signature = inspect.getargspec(func)
    except TypeError:  # if function isn't python function we can not know about it
        return func

    if 0 < len(signature.args) < 2:
        return func

    raise TypeError(
        'Incorrect signature of function "{0}" -> "{1}". Should be "{0}" -> "[\'instance\']".'.format(
            pyv.get_func_name(func), str(signature.args),

        ),
    )
