# -*- coding: utf-8 -*-

import inspect

from . import signature
from ...utils import pyv
from .exceptions import BuildError
from .exceptions import ValidationError


class AliasToMethod(object):

    def __init__(self, option_name, method_name):
        self._option_name = option_name
        self._method_name = method_name

    @property
    def option_name(self):
        return self._option_name

    @property
    def method_name(self):
        return self._method_name


class FactoryMethodWrapper(object):

    def __init__(self, parent_sig, option_name, method_name):
        self._option_name = option_name
        self._method_name = method_name
        self._option_value = parent_sig.kwargs.pop(self._option_name, None)

    def __repr__(self):
        return '{}: {}->{}'.format(
            self.__class__.__name__, self._option_name, self._method_name,
        )

    def __call__(self, factory_instance):
        if self._option_value is None:
            return

        method = getattr(factory_instance, self._method_name)

        for sig in signature.create_signatures(self._option_value):
            method(*sig.args, **sig.kwargs)


def _approve_alias(data):
    if isinstance(data, AliasToMethod):
        return data
    if isinstance(data, (list, tuple)):
        option_name, method_name = data
        return AliasToMethod(option_name, method_name)
    elif isinstance(data, pyv.basestring):
        return AliasToMethod(data, data)

    raise BuildError('Incorrect pre/post staging data "{}"'.format(data))


def create_factory_methods(sig, staging):
    pre_methods = []
    post_methods = []

    for alias in staging.get('pre', []):
        alias = _approve_alias(alias)
        pre_methods.append(
            FactoryMethodWrapper(sig, alias.option_name, alias.method_name),
        )

    for alias in staging.get('post', []):
        alias = _approve_alias(alias)
        post_methods.append(
            FactoryMethodWrapper(sig, alias.option_name, alias.method_name),
        )

    return pre_methods, post_methods


def call_to_methods(methods, factory_instance):
    for method_wrapper in methods:
        method_wrapper(factory_instance)


def declare_creator_callback(creator):
    if not callable(creator):
        return creator

    sig = inspect.getargspec(creator)

    if len(sig.args) != 2:
        raise ValidationError(
            'Incorrect signature on creator callback {} Should be {}'.format(
                sig.args, ['factory', 'schema'],
            ),
        )

    return creator


class Staging(object):

    def __init__(self, compiled_rule):
        self._pre_methods, self._post_methods = create_factory_methods(
            compiled_rule.sig, compiled_rule.staging,
        )

        if callable(compiled_rule.initializer):
            self._factory = compiled_rule.initializer(
                compiled_rule.builder, compiled_rule.factory_class, compiled_rule.sig,
            )
        else:
            self._factory = compiled_rule.factory_class(
                *compiled_rule.sig.args, **compiled_rule.sig.kwargs
            )

        self._embedded_instance = None
        self._compiled_rule = compiled_rule

    @property
    def factory(self):
        return self._factory

    @property
    def embedded_instance(self):
        return self._embedded_instance

    def pre(self):
        call_to_methods(self._pre_methods, self._factory)

    def create(self):
        creator = declare_creator_callback(
            self._compiled_rule.staging.get('creator'),
        )

        if callable(creator):
            originated = creator(self._factory, self._compiled_rule.instance)
        else:
            originated = self._factory.create()

        self._embedded_instance = self._compiled_rule.builder.__schema_class__(
            self._compiled_rule.name, originated, self._factory,
        )
        instance_name = self._compiled_rule.property_name or self._compiled_rule.name
        self._compiled_rule.instance[instance_name] = self._embedded_instance

        if self._compiled_rule.storage_name:
            if self._compiled_rule.storage_name not in self._compiled_rule.instance:
                self._compiled_rule.instance[self._compiled_rule.storage_name] = []

            self._compiled_rule.instance[self._compiled_rule.storage_name].append(self._embedded_instance)

    def post(self):
        call_to_methods(self._post_methods, self._factory)
