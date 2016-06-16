# -*- coding: utf-8 -*-

from . import collector
from .rule import SettingsValue
from .staging import AliasToMethod
from .signature import Signature as sig
from .exceptions import ConfigurationError


class BuilderSchema(object):

    def __init__(self, name, obj=None, factory=None):
        self.__obj = obj
        self.__name = name
        self.__factory = factory

    def __getattr__(self, item):
        try:
            return getattr(self.__factory, item)
        except AttributeError:
            pass

        try:
            return getattr(self.__obj, item)
        except AttributeError:
            pass

        raise AttributeError('{}: {}'.format(self.__class__.__name__, item))

    def __contains__(self, item):
        return item in self.__dict__

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        if self.__obj and self.__factory:
            return '<Schema({} spawned {}): {}>'.format(
                self.__factory.__class__.__name__, self.__obj.__class__.__name__, self.__name,
            )
        return '<Schema: {}>'.format(self.__name)

    def __dir__(self):
        self_dir = [k for k in self.__dict__ if not k.startswith('_')]

        return list(
            set(
                dir(self.__obj) + dir(self.__factory) + self_dir
            ),
        )


class BaseBuilderSettings(object):

    def __init__(self, **options):
        self.__options = options

    @property
    def options(self):
        return self.__options


class BaseBuilder(object):

    __build_schema__ = {}
    __schema_class__ = BuilderSchema
    __settings_class__ = BaseBuilderSettings

    def __init__(self, case):
        self.case = case
        self._schema = None
        self._settings = None

    @property
    def schema(self):
        return self._schema

    @property
    def settings(self):
        return self._settings

    def configure(self, **kwargs):
        self._settings = self.__settings_class__(**kwargs)

    def build(self):
        if not self._settings:
            raise ConfigurationError(
                'Builder was not configured. Should to configure builder for this operation.',
            )

        self._schema = self.__schema_class__('general')

        collector.collect(self)


__all__ = (
    'sig',
    'BaseBuilder',
    'AliasToMethod',
    'BuilderSchema',
    'SettingsValue',
    'BaseBuilderSettings',
)
