# -*- coding: utf-8 -*-

from copy import deepcopy

from .exceptions import ExtensionNotFound


_TMP = {}
_WAS_CLEAR = False


def install(ext, program):
    if getattr(ext, '__install__', None):
        ext.__install__(program)


def add_options(ext, parser):
    if getattr(ext, '__add_options__', None):
        ext.__add_options__(parser)


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

    def __init__(self, *args, **kwargs):
        super(SingletonExtensionContainer, self).__init__(*args, **kwargs)

        self.__instance = None

    def __call__(self):
        if self.__instance is None:
            self.__instance = super(
                SingletonExtensionContainer, self,
            ).__call__()
        return self.__instance


def get(name):
    try:
        container = _TMP[name]
    except KeyError:
        if _WAS_CLEAR:
            raise RuntimeError(
                'Extension tmp was cleared',
            )
        raise ExtensionNotFound(name)

    if isinstance(container, ExtensionContainer):
        return container()

    return deepcopy(container)


def set(ext, name, is_data=False, singleton=False, args=None, kwargs=None):
    if is_data:
        _TMP[name] = ext
    else:
        if singleton:
            _TMP[name] = SingletonExtensionContainer(
                ext, args=args, kwargs=kwargs,
            )
        else:
            _TMP[name] = ExtensionContainer(
                ext, args=args, kwargs=kwargs,
            )


def clear():
    global _WAS_CLEAR

    _TMP.clear()
    _WAS_CLEAR = True
