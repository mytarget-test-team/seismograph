# -*- coding: utf-8 -*-

from ...utils import pyv
from .exceptions import ConfigurationError


class Signature(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def create_signatures(option_value):
    def create_signature(v):
        if isinstance(v, Signature):
            return v

        if isinstance(v, dict):
            return Signature(**v)
        elif v is True:
            return Signature()

        raise ConfigurationError(
            'Can not create signature from option value {}'.format(v),
        )

    if type(option_value) is int:
        return map(lambda i: Signature(), pyv.xrange(option_value))

    if isinstance(option_value, (list, tuple)):
        return map(create_signature, option_value)

    return [create_signature(option_value)]
