# -*- coding: utf-8 -*-

from seismograph import Suite, Case, CaseLayer


suite = Suite(__name__)


class ExampleCaseLayer(CaseLayer):

    def on_init(self, case):
        setattr(case, 'on_init_was_call', True)

    def on_setup(self, case):
        if not case.config.VERBOSE:
            case.print_hello()

    def on_teardown(self, case):
        if not case.config.VERBOSE:
            case.print_bye()

    def on_run(self, case):
        setattr(case, 'on_run_was_call', True)

    # for example
    def on_skip(self, case, reason, result):
        pass

    def on_any_error(self, error, case, result):
        pass

    def on_error(self, error, case, result):
        pass

    def on_context_error(self, error, case, result):
        pass

    def on_fail(self, fail, case, result):
        pass

    def on_success(self, case):
        pass


@suite.register
class ExampleCase(Case):

    __layers__ = (
        ExampleCaseLayer(),
    )

    def print_hello(self):
        """Hello"""
        pass

    def print_bye(self):
        """Good bye"""
        pass

    def test(self):
        self.assertion.true(hasattr(self, 'on_init_was_call'))
        self.assertion.true(hasattr(self, 'on_run_was_call'))
