# -*- coding: utf-8 -*-

import abc
from functools import wraps

from six import with_metaclass

from ...utils import pyv
from .exceptions import RestrictionError


FACTORY_METHOD_PREFIX = 'create_'


def _set_storage_name(method, storage_name):
    setattr(method, '__storage_name__', storage_name)


def _get_storage_name(method, default):
    return getattr(method, '__storage_name__', default)


def _get_default_storage_name(method_name):
    return method_name.replace(FACTORY_METHOD_PREFIX, '')


def _set_required(f, *what):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        for it in what:
            if not getattr(self, it):
                raise RestrictionError(
                    'Method "{}" from class "{}" can not be called. "{}" is required.'.format(
                        pyv.get_func_name(f),
                        self.__class__.__name__,
                        it,
                    ),
                )

        return f(self, *args, **kwargs)
    return wrapper


def _set_only_one_creation(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        method_name = pyv.get_func_name(f)
        storage_name = _get_storage_name(
            f, _get_default_storage_name(method_name),
        )

        if getattr(self, storage_name) is not None:
            raise RestrictionError(
                '"{}" already created on {}'.format(
                    storage_name, self,
                ),
            )

        return f(self, *args, **kwargs)
    return wrapper


def factory_method(**options):
    def wrapper(f):
        required = options.pop('required', None)
        storage = options.pop('storage', None)
        only_one_creation = options.pop('only_one_creation', None)

        if options:
            raise TypeError(
                'got an unexpected keyword arguments "{}"'.format(
                    ', '.join(options.keys()),
                ),
            )

        if storage:
            _set_storage_name(f, storage)

        if only_one_creation:
            f = _set_only_one_creation(f)

        if required:
            if not isinstance(required, (list, tuple)):
                required = (required, )

            f = _set_required(f, *required)

        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped
    return wrapper


class FactoryMeta(abc.ABCMeta):

    def __new__(mcs, *args, **kwargs):
        cls = abc.ABCMeta.__new__(mcs, *args, **kwargs)
        attributes = list(n for n in dir(cls) if not n.startswith('_'))
        factory_methods = filter(lambda n: n.startswith(FACTORY_METHOD_PREFIX), attributes)

        for method_name in factory_methods:
            storage_name = _get_storage_name(
                getattr(cls, method_name),
                _get_default_storage_name(method_name),
            )

            if storage_name not in attributes:
                raise RestrictionError(
                    'Class "{}" has method "{}" but does not has property "{}"'.format(
                        cls.__name__,
                        method_name,
                        storage_name,
                    ),
                )

        return cls


class BaseFactory(with_metaclass(FactoryMeta, object)):

    @abc.abstractproperty
    def data(self):
        pass

    @abc.abstractmethod
    def build_data(self, **data):
        pass

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    @property
    def factory_methods(self):
        return sorted(
            list(
                filter(lambda n: n.startswith(FACTORY_METHOD_PREFIX), dir(self)),
            ),
        )
