# -*- coding: utf-8 -*-

"""
Default groups for simple run
"""

from .. import runnable


class DefaultSuiteGroup(runnable.RunnableGroup):

    def run(self, result):
        for suite in self.objects:
            suite(result)


class DefaultCaseGroup(runnable.RunnableGroup):

    def run(self, result):
        for case in self.objects:
            case(result)
