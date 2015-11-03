# -*- coding: utf-8 -*-

from seismograph import Suite, Case


suite = Suite(__name__)


@suite.add_setup
def setup():
    if not suite.config.VERBOSE:
        'suite setup'


@suite.add_teardown
def teardown():
    if not suite.config.VERBOSE:
        'suite teardown'


@suite.register
def test_of_suite(case):
    case.assertion.true(True)


class SuiteSetupTearDownExample(Suite):

    def setup(self):
        if not self.config.VERBOSE:
            'my suite setup'

    def teardown(self):
        if not self.config.VERBOSE:
            'my suite teardown'


my_suite = SuiteSetupTearDownExample(__name__ + '.setup_teardown_example')


@my_suite.register
def test_of_suite(case):
    case.assertion.true(True)


@my_suite.register
class CaseSetupTearDownExample(Case):

    def setup(self):
        if not self.config.VERBOSE:
            'my case setup'

    def teardown(self):
        if not self.config.VERBOSE:
            'my case teardown'

    def test(self):
        self.assertion.false(False)


if __name__ == '__main__':
    import seismograph
    seismograph.main()
