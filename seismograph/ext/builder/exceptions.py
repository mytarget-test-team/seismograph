# -*- coding: utf-8 -*-

from ...exceptions import SeismographError


class BaseBuilderError(SeismographError):
    pass


class ConfigurationError(BaseBuilderError):
    pass


class SchemaError(BaseBuilderError):
    pass


class FactoryError(BaseBuilderError):
    pass


class RestrictionError(FactoryError):
    pass


class ValidationError(BaseBuilderError):
    pass


class BuildError(BaseBuilderError):
    pass


class RelationError(SchemaError):
    pass
