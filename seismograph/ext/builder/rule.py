# -*- coding: utf-8 -*-

import types
import inspect
from jsonschema import Draft4Validator
from jsonschema import ValidationError as JsonSchemaValidationError

from ...utils import pyv
from .exceptions import ValidationError
from .factory import FactoryMeta as FactoryType


SCHEMA = {
    'type': 'object',
    'properties': {
        'storage': {'type': 'string'},
        'embedded': {'type': 'object'},
        'initializer': {'type': 'function'},
        'factory_class': {'type': 'factory'},
        'staging': {
            'type': 'object',
            'properties': {
                'creator': {'type': 'function'},
                'pre': {'type': ['list', 'tuple']},
                'post': {'type': ['list', 'tuple']},
            },
        },
        'require': {'type': 'array'},
    },
    'required': ['factory_class'],
}


class SchemaValidator(Draft4Validator):

    DEFAULT_TYPES = Draft4Validator.DEFAULT_TYPES

    DEFAULT_TYPES.update(**{
        'list': list,
        'tuple': tuple,
        'factory': FactoryType,
        'function': types.FunctionType,
    })

    def __init__(self, schema):
        super(SchemaValidator, self).__init__(SCHEMA)
        try:
            self.validate(schema)
        except JsonSchemaValidationError as error:
            raise ValidationError(pyv.get_exc_message(error))


class SettingsValue(str):
    pass


def _get_value(schema, settings, key):
    value = schema.get(key)
    if isinstance(value, SettingsValue):
        return getattr(settings, value)
    return value


def declare_initializer_callback(initializer):
    if not callable(initializer):
        return initializer

    sig = inspect.getargspec(initializer)

    if len(sig.args) != 3:
        raise ValidationError(
            'Incorrect signature on initializer callback {} Should be {}'.format(
                sig.args, ['builder', 'cls', 'sig'],
            ),
        )

    return initializer


class RuleObject(object):

    def __init__(self, name, builder, schema, instance):
        SchemaValidator(schema)

        self._name = name
        self._schema = schema
        self._builder = builder
        self._instance = instance

        self._require = schema.get('require', [])
        self._staging = schema.get('staging', {})
        self._storage_name = schema.get('storage')
        self._property_name = schema.get('property')
        self._embedded_schema = schema.get('embedded', {})
        self._initializer = declare_initializer_callback(
            _get_value(schema, builder.settings, 'initializer'),
        )
        self._factory_class = _get_value(schema, builder.settings, 'factory_class')

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self._name)

    @property
    def name(self):
        return self._name

    @property
    def schema(self):
        return self._schema

    @property
    def builder(self):
        return self._builder

    @property
    def instance(self):
        return self._instance

    @property
    def require(self):
        return self._require

    @property
    def storage_name(self):
        return self._storage_name

    @property
    def staging(self):
        return self._staging

    @property
    def property_name(self):
        return self._property_name

    @property
    def embedded_schema(self):
        return self._embedded_schema

    @property
    def initializer(self):
        return self._initializer

    @property
    def factory_class(self):
        return self._factory_class

    @property
    def can_be_compiled(self):
        return all(r in self._instance for r in self._require)

    def get_current_requires(self):
        return [r for r in self._require if r not in self._instance]

    def compile(self, sig):
        if self._embedded_schema:
            embedded_options = dict(
                (k, sig.kwargs.pop(k))
                for k in self._embedded_schema.keys()
                if sig.kwargs.get(k) is not None
            )
        else:
            embedded_options = {}

        return CompiledRule(
            sig=sig,
            name=self._name,
            builder=self._builder,
            require=self._require,
            staging=self._staging,
            instance=self._instance,
            initializer=self._initializer,
            storage_name=self._storage_name,
            property_name=self._property_name,
            factory_class=self._factory_class,
            embedded_options=embedded_options,
            embedded_schema=self._embedded_schema,
        )


class CompiledRule(object):

    def __init__(self,
                 sig=None,
                 name=None,
                 builder=None,
                 require=None,
                 instance=None,
                 staging=None,
                 initializer=None,
                 storage_name=None,
                 property_name=None,
                 factory_class=None,
                 embedded_schema=None,
                 embedded_options=None):
        self._sig = sig
        self._name = name
        self._builder = builder
        self._require = require
        self._staging = staging
        self._instance = instance
        self._initializer = initializer
        self._storage_name = storage_name
        self._property_name = property_name
        self._factory_class = factory_class
        self._embedded_schema = embedded_schema
        self._embedded_options = embedded_options

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self._name)

    @property
    def sig(self):
        return self._sig

    @property
    def name(self):
        return self._name

    @property
    def builder(self):
        return self._builder

    @property
    def instance(self):
        return self._instance

    @property
    def require(self):
        return self._require

    @property
    def storage_name(self):
        return self._storage_name

    @property
    def staging(self):
        return self._staging

    @property
    def property_name(self):
        return self._property_name

    @property
    def embedded_schema(self):
        return self._embedded_schema

    @property
    def initializer(self):
        return self._initializer

    @property
    def factory_class(self):
        return self._factory_class

    @property
    def embedded_options(self):
        return self._embedded_options
