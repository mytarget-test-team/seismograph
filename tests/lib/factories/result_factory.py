# -*- coding: utf-8 -*-

from StringIO import StringIO
from seismograph.result import Result


def create(config, **kwargs):
    kwargs.setdefault('stream', StringIO())
    return Result(config, **kwargs)
