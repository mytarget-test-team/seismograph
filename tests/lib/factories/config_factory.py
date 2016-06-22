# -*- coding: utf-8 -*-

import time


class FakeConfig(object):

    def __init__(self):
        self.XUNIT_REPORT = None
        self.VERBOSE = False
        self.OUTPUT = None
        self.NO_CAPTURE = False
        self.SUITE_DETAIL = False
        self.TREE = False
        self.NO_COLOR = False
        self.STEPS_LOG = False
        self.FLOWS_LOG = False
        self.STEP_BY_STEP = False
        self.TESTS = []
        self.INCLUDE_SUITES_PATTERN = None
        self.EXCLUDE_SUITE_PATTERN = None
        self.STOP = False
        self.REPEAT = 0
        self.RANDOM = False
        self.RANDOM_SEED = time.time()
        self.NO_SCRIPTS = False
        self.ASYNC_SUITES = 0
        self.ASYNC_TESTS = 0
        self.MULTIPROCESSING_TIMEOUT = 1800.0
        self.GEVENT = False
        self.THREADING = False
        self.MULTIPROCESSING = False
        self.PDB = False

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
