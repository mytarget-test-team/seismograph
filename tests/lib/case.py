# -*- coding: utf-8 -*-

import unittest

from ..factories import case_factory
from ..factories import config_factory
from ..factories import result_factory


class BaseTestCase(unittest.TestCase):
    pass


class ConfigTestCaseMixin(object):

    __config_options__ = {}

    def setUp(self):
        super(ConfigTestCaseMixin, self).setUp()

        self.config = config_factory.create(**self.__config_options__)

    def tearDown(self):
        super(ConfigTestCaseMixin, self).tearDown()

        self.config = None


class ResultTestCaseMixin(object):

    def setUp(self):
        super(ResultTestCaseMixin, self).setUp()

        self.result = result_factory.create(self.config)

    def tearDown(self):
        super(ResultTestCaseMixin, self).tearDown()

        self.result = None


class CaseTestCaseMixin(ResultTestCaseMixin, ConfigTestCaseMixin):

    __config_options__ = {}

    class CaseClass(case_factory.EmptyCase):
        pass

    def setUp(self):
        super(CaseTestCaseMixin, self).setUp()

        self.create_case()

    def tearDown(self):
        super(CaseTestCaseMixin, self).tearDown()

        self.case = None

    def create_case(self):
        self.case = self.CaseClass('test', config=self.config)


class RunCaseTestCaseMixin(CaseTestCaseMixin):

    def setUp(self):
        super(RunCaseTestCaseMixin, self).setUp()

        self.run_case()

    def run_case(self):
        self.case(self.result)
