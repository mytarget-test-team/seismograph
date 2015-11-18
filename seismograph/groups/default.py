# -*- coding: utf-8 -*-

"""
Default groups for simple run
"""

from .. import runnable


class DefaultSuiteGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        for suite in self.objects:
            suite(result)


class DefaultCaseGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        for case in self.objects:
            case(result)
