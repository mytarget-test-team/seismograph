# -*- coding: utf-8 -*-

from seismograph import ProgramLayer as _ProgramLayer
from seismograph import CaseLayer as _CaseLayer
from seismograph import SuiteLayer as _SuiteLayer


class ProgramLayer(_ProgramLayer):

    def __init__(self):
        super(ProgramLayer, self).__init__()
        self.was_called = None
        self.counter = 0
        self.calling_story = []

    def on_init(self, program):
        self.was_called = 'on_init'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_config(self, config):
        self.was_called = 'on_config'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_setup(self, program):
        self.was_called = 'on_setup'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_teardown(self, program):
        self.was_called = 'on_teardown'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_error(self, error, program, result, tb, timer):
        self.was_called = 'on_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_option_parser(self, parser):
        self.was_called = 'on_option_parser'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_run(self, program):
        self.was_called = 'on_run'
        self.counter += 1
        self.calling_story.append(self.was_called)


class SuiteLayer(_SuiteLayer):

    def __init__(self):
        super(SuiteLayer, self).__init__()
        self.was_called = None
        self.counter = 0
        self.calling_story = []

    def on_init(self, suite):
        self.was_called = 'on_init'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_require(self, require):
        self.was_called = 'on_require'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_build_rule(self, suite, rule):
        self.was_called = 'on_build_rule'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_setup(self, suite):
        self.was_called = 'on_setup'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_teardown(self, suite):
        self.was_called = 'on_teardown'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_mount(self, suite, program):
        self.was_called = 'on_mount'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_run(self, suite):
        self.was_called = 'on_run'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_error(self, error, suite, result, tb, timer):
        self.was_called = 'on_error'
        self.counter += 1
        self.calling_story.append(self.was_called)


class CaseLayer(_CaseLayer):

    def __init__(self):
        super(CaseLayer, self).__init__()
        self.was_called = None
        self.counter = 0
        self.calling_story = []

    def on_init(self, case):
        self.was_called = 'on_init'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_require(self, require):
        self.was_called = 'on_require'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_setup(self, case):
        self.was_called = 'on_setup'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_teardown(self, case):
        self.was_called = 'on_teardown'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_skip(self, case, reason, result):
        self.was_called = 'on_skip'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_any_error(self, error, case, result, tb, timer):
        self.was_called = 'on_any_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_error(self, error, case, result, tb, timer):
        self.was_called = 'on_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_context_error(self, error, case, result, tb, timer):
        self.was_called = 'on_context_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_fail(self, fail, case, result, tb, timer):
        self.was_called = 'on_fail'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_success(self, case, *args):
        self.was_called = 'on_success'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_run(self, case):
        self.was_called = 'on_run'
        self.counter += 1
        self.calling_story.append(self.was_called)
