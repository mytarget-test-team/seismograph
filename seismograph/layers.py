# -*- coding: utf-8 -*-

from . import runnable


class CaseLayer(runnable.LayerOfRunnableObject):

    def on_init(self, case):
        """
        :type case: Case
        """
        pass

    def on_require(self, require):
        """
        :type require: list
        """
        pass

    def on_setup(self, case):
        """
        :type case: Case
        """
        pass

    def on_teardown(self, case):
        """
        :type case: Case
        """
        pass

    def on_skip(self, case, reason, result):
        """
        :type case: Case
        :type reason: str
        :type result: seismograph.result.Result
        """
        pass

    def on_any_error(self, error, case, result, tb, timer):
        """
        :type case: Case
        :type error: BaseException
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass

    def on_error(self, error, case, result, tb, timer):
        """
        :type case: Case
        :type error: BaseException
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass

    def on_context_error(self, error, case, result, tb, timer):
        """
        :type case: Case
        :type error: BaseException
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass

    def on_fail(self, fail, case, result, tb, timer):
        """
        :type case: Case
        :type fail: AssertionError
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass

    def on_success(self, case, timer):
        """
        :type case: Case
        """
        pass

    def on_run(self, case):
        """
        :type case: Case
        """
        pass


class SuiteLayer(runnable.LayerOfRunnableObject):

    def on_init(self, suite):
        """
        :type suite: Suite
        """
        pass

    def on_require(self, require):
        """
        :type require: list
        """
        pass

    def on_build_rule(self, suite, rule):
        """
        :type suite: Suite
        :type rule: BuildRule
        """
        pass

    def on_setup(self, suite):
        """
        :type suite: Suite
        """
        pass

    def on_teardown(self, suite):
        """
        :type suite: Suite
        """
        pass

    def on_mount(self, suite, program):
        """
        :type suite: Suite
        :type program: seismograph.program.Program
        """
        pass

    def on_run(self, suite):
        """
        :type suite: Suite
        """
        pass

    def on_error(self, error, suite, result, tb, timer):
        """
        :type error: BaseException
        :type suite: Suite
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass


class ProgramLayer(runnable.LayerOfRunnableObject):

    def on_init(self, program):
        """
        :type program: Program
        """
        pass

    def on_config(self, config):
        """
        :type config: seismograph.config.Config
        """
        pass

    def on_setup(self, program):
        """
        :type program: Program
        """
        pass

    def on_teardown(self, program):
        """
        :type program: Program
        """
        pass

    def on_error(self, error, program, result, tb, timer):
        """
        :type error: BaseException
        :type program: Program
        :type result: seismograph.result.Result
        :type tb: str
        :type timer: callable
        """
        pass

    def on_option_parser(self, parser):
        """
        :param parser: optparse.OptionParser
        """
        pass

    def on_run(self, program):
        """
        :type program: Program
        """
        pass
