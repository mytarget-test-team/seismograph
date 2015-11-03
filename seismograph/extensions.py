# -*- coding: utf-8 -*-

from copy import deepcopy

from .exceptions import ExtensionNotFound


_TMP = {}


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


def install(ext, program):
    assert isinstance(ext, BaseExtension)
    ext.__install__(program)


def get(name, singleton=False):
    try:
        ext = _TMP[name]
    except KeyError:
        raise ExtensionNotFound(name)

    if isinstance(ext, ExtensionContainer):
        if singleton:
            if not isinstance(ext, SingletonExtensionContainer):
                ext = SingletonExtensionContainer(ext())
                _TMP[name] = ext
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
