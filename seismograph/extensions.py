# -*- coding: utf-8 -*-

from copy import deepcopy

from .exceptions import ExtensionNotFound


_TMP = {}


def install(ext, program):
    assert isinstance(ext, BaseExtension), \
        '"{}" is not instance of "BaseExtension"'.format(
            ext.__class__.__name__,
        )
    ext.__install__(program)


def add_options(ext, parser):
    ext.__add_options__(parser)


class BaseExtension(object):

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(
            'Method "__call__" not implemented in "{}.{}"'.format(
                self.__class__.__module__, self.__class__.__name__,
            ),
        )

    def __install__(self, program):
        raise NotImplementedError(
            'Method "__install__" not implemented in "{}.{}"'.format(
                self.__class__.__module__, self.__class__.__name__,
            ),
        )

    @staticmethod
    def __add_options__(parser):
        pass


class ExtensionContainer(object):

    def __init__(self, ext, args=None, kwargs=None):
        self.__ext = ext
        self.__args = args or tuple()
        self.__kwargs = kwargs or dict()

    def __call__(self):
        return self.__ext(*self.__args, **self.__kwargs)

    @property
    def ext(self):
        return self.__ext

    @property
    def args(self):
        return self.__args

    @property
    def kwargs(self):
        return self.__kwargs


class SingletonExtensionContainer(ExtensionContainer):

    def __call__(self):
        return self.ext


def get(name):
    try:
        ext = _TMP[name]
    except KeyError:
        raise ExtensionNotFound(name)

    if isinstance(ext, ExtensionContainer):
        return ext()

    return deepcopy(ext)


def set(ext, name, is_data=False, singleton=False, args=None, kwargs=None):
    if is_data:
        _TMP[name] = ext
    else:
        if singleton:
            _TMP[name] = SingletonExtensionContainer(
                ext(*(args or tuple()), **(kwargs or dict())),
            )
        else:
            _TMP[name] = ExtensionContainer(ext, args=args, kwargs=kwargs)


def clear():
    _TMP.clear()
