# -*- coding: utf-8 -*-

import unittest
from StringIO import StringIO

from .factories import case_factory
from .factories import suite_factory
from .factories import config_factory
from .factories import result_factory


class BaseTestCase(unittest.TestCase):

    maxDiff = None


class ConfigTestCaseMixin(object):

    __config_options__ = {}

    def setUp(self):
        super(ConfigTestCaseMixin, self).setUp()

        self.make_config()

    def tearDown(self):
        super(ConfigTestCaseMixin, self).tearDown()

        self.config = None

    def make_config(self):
        self.config = config_factory.create(**self.__config_options__)


class ResultTestCaseMixin(ConfigTestCaseMixin):

    __stream__ = None

    def setUp(self):
        super(ResultTestCaseMixin, self).setUp()

        self.make_result()

    def tearDown(self):
        super(ResultTestCaseMixin, self).tearDown()

        self.result = None
        self.stream = None

    def make_result(self):
        self.stream = self.__stream__ or StringIO()
        self.result = result_factory.create(self.config, stream=self.stream)


class CaseTestCaseMixin(ResultTestCaseMixin):

    __config_options__ = {}

    class CaseClass(case_factory.FakeCase):
        pass

    def setUp(self):
        super(CaseTestCaseMixin, self).setUp()

        self.make_case()

    def tearDown(self):
        super(CaseTestCaseMixin, self).tearDown()

        self.case = None

    def make_case(self):
        self.case = self.CaseClass('test', config=self.config)


class SuiteTestCaseMixin(ConfigTestCaseMixin):

    class SuiteClass(suite_factory.FakeSuite):
        pass

    def setUp(self):
        super(SuiteTestCaseMixin, self).setUp()

        self.make_suite()

    def tearDown(self):
        super(SuiteTestCaseMixin, self).tearDown()

        self.suite = None

    def make_suite(self):
        self.suite = suite_factory.create(
            config=self.config,
            suite_class=self.SuiteClass,
        )


class RunSuiteTestCaseMixin(CaseTestCaseMixin, SuiteTestCaseMixin):

    def setUp(self):
        super(RunSuiteTestCaseMixin, self).setUp()

        self.suite.cases.append(self.CaseClass)
        self.suite.build()
        self.run_suite()

    def run_suite(self):
        self.suite(self.result)


class RunCaseTestCaseMixin(CaseTestCaseMixin):

    def setUp(self):
        super(RunCaseTestCaseMixin, self).setUp()

        self.run_case()

    def run_case(self):
        self.case(self.result)
