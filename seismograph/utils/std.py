# -*- coding: utf-8 -*-

import sys

try:
    from StringIO import StringIO
except ImportError:  # please python 3
    from io import StringIO

from contextlib import contextmanager


@contextmanager
def dev_null():
    class MockStd(object):

        def __getattr__(self, item):
            def null(*args, **kwargs):
                pass
            return null

    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = MockStd()
    sys.stderr = MockStd()
    try:
        yield
    finally:
        sys.stdout = stdout
        sys.stderr = stderr


@contextmanager
def capture_stdout(stream=None):
    stream = stream or StringIO()
    stdout = sys.stdout
    sys.stdout = stream
    try:
        yield stream
    finally:
        sys.stdout = stdout


@contextmanager
def capture_stderr(stream=None):
    stream = stream or StringIO()
    stderr = sys.stderr
    sys.stderr = stream
    try:
        yield stream
    finally:
        sys.stderr = stderr


@contextmanager
def capture_output(stream=None):
    stream = stream or StringIO()
    with capture_stdout(stream):
        with capture_stderr(stream):
                yield stream
