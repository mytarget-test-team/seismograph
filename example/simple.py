# -*- coding: utf-8 -*-

from seismograph import Case, Suite, assertion


suite = Suite(__name__)


@suite.register
class ExampleTestCase(Case):

    def test_false(self):
        self.assertion.false(False)


@suite.register
def example_function_test(case):
    case.assertion.true(True)


@suite.register(static=True)
def example_static_function_test():
    assertion.true(True)
