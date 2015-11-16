# -*- coding: utf-8 -*-

from ...exceptions import SeismographError


class AlchemyError(SeismographError):
    pass


class ConfigurationError(AlchemyError):
    pass


class NotFound(AlchemyError):
    pass


class InvalidBindKey(AlchemyError):
    pass
