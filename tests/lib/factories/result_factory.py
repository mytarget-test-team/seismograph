# -*- coding: utf-8 -*-

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from seismograph.result import Result


def create(config, **kwargs):
    kwargs.setdefault('stream', StringIO())
    return Result(config, **kwargs)
