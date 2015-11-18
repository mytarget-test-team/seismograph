# -*- coding: utf-8 -*-

import sys
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
