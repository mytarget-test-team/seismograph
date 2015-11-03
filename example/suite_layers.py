# -*- coding: utf-8 -*-

from seismograph import Suite, SuiteLayer


class SuiteLayerExample(SuiteLayer):

    def on_init(self, suite):
        setattr(suite, 'on_init_was_call', True)

    def on_mount(self, suite, program):
        if not suite.config.VERBOSE:
            'suite "{}" is mounted'.format(suite.name)
        setattr(suite, 'on_mount_was_call', True)

    def on_run(self, suite):
        setattr(suite, 'on_run_was_call', True)

    def on_setup(self, suite):
        if not suite.config.VERBOSE:
            'on_setup from suite layer'

    def on_teardown(self, suite):
        if not suite.config.VERBOSE:
            'on_teardown from suite layer'

    # for example
    def on_any_error(self, error, suite, result):
        pass

    def on_error(self, error, suite, result):
        pass

    def on_context_error(self, error, suite, result):
        pass


suite = Suite(__name__, layers=[SuiteLayerExample()])


@suite.register
def test_of_suite(case):
    case.assertion.true(hasattr(suite, 'on_init_was_call'))
    case.assertion.true(hasattr(suite, 'on_mount_was_call'))
    case.assertion.true(hasattr(suite, 'on_run_was_call'))


class ExampleSuite(Suite):

    __layers__ = (
        SuiteLayerExample(),
    )


my_suite = ExampleSuite(__name__ + '.example_suite')


@my_suite.register
def test_of_my_uite(case):
    case.assertion.true(hasattr(my_suite, 'on_init_was_call'))
    case.assertion.true(hasattr(my_suite, 'on_mount_was_call'))
    case.assertion.true(hasattr(my_suite, 'on_run_was_call'))


if __name__ == '__main__':
    import seismograph
    seismograph.main()
