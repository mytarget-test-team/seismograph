# -*- coding: utf-8 -*-

import time


class FakeConfig(object):

    XUNIT_REPORT = None
    VERBOSE = False
    OUTPUT = None
    NO_CAPTURE = False
    SUITE_DETAIL = False
    TREE = False
    NO_COLOR = False
    STEPS_LOG = False
    FLOWS_LOG = False
    STEP_BY_STEP = False
    TESTS = []
    INCLUDE_SUITES_PATTERN = None
    EXCLUDE_SUITE_PATTERN = None
    STOP = False
    REPEAT = 0
    RANDOM = False
    RANDOM_SEED = time.time()
    NO_SCRIPTS = False
    ASYNC_SUITES = 0
    ASYNC_TESTS = 0
    MULTIPROCESSING_TIMEOUT = 1800.0
    GEVENT = False
    THREADING = False
    MULTIPROCESSING = False

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def get(self, key):
        return getattr(self, key, None)


def create(**kwargs):
    config = FakeConfig()
    if kwargs:
        for k, v in kwargs.items():
            setattr(config, k, v)
    return config
