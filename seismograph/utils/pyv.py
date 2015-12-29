# -*- coding: utf-8 -*-

"""
Module for supporting py 2-3 versions.
"""

import sys
import types

from ..exceptions import PyVersionError


IS_PYTHON_3 = sys.version_info >= (3, 0)
IS_PYTHON_2 = not IS_PYTHON_3


def check_py_version():
    error_mess = 'Unsupported py version. Need python 2.7 and greater.'

    if not IS_PYTHON_3 and not IS_PYTHON_2:
        raise PyVersionError(error_mess)

    if sys.version_info < (2, 7):
        raise PyVersionError(error_mess)


def check_gevent_supported():
    if IS_PYTHON_3:
        raise PyVersionError('gevent lib not supported with python 3')


if IS_PYTHON_2:
    basestring = basestring
elif IS_PYTHON_3:
    basestring = str


if IS_PYTHON_2:
    unicode = unicode
elif IS_PYTHON_3:
    unicode = str


if IS_PYTHON_2:
    xrange = xrange
elif IS_PYTHON_3:
    xrange = range


if IS_PYTHON_2:
    reduce = reduce
elif IS_PYTHON_3:
    from functools import reduce
    reduce = reduce


if IS_PYTHON_2:
    execfile = execfile
elif IS_PYTHON_3:
    def execfile(filename, globals=None, locals=None):
        with open(filename, 'r') as fp:
            exec(fp.read(), globals, locals)


def get_exc_message(error):
    if hasattr(error, 'message'):
        return error.message

    return u''.join((unicode_string(m) for m in error.args))


def get_func_name(func):
    __func__ = getattr(func, '__func__', None)
    if __func__ is not None:
        return __func__.__name__

    return func.__name__


def is_class_type(obj):
    if IS_PYTHON_2:
        return isinstance(obj, (type, types.ClassType))

    return isinstance(obj, type)


def unicode_string(string):
    try:
        return unicode(string)
    except UnicodeDecodeError as error:
        if IS_PYTHON_2:
            return unicode(string.decode('utf-8'))
        raise error
