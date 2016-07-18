# -*- coding: utf-8 -*-

import traceback

from . import runnable
from .utils.common import measure_time


class Script(runnable.RunnableObject):

    __run_point__ = None
    __stop_if_error__ = False
    __create_reason__ = False

    def __init__(self, program):
        super(Script, self).__init__()

        self._timer = None
        self.__program = program

    def __str__(self):
        return 'script ({}.{})'.format(
            self.__class__.__module__,
            self.__class__.__name__,
        )

    def __is_run__(self):
        return True

    @property
    def config(self):
        return self.__program.config

    @property
    def ext(self):
        return self.__program.ext

    def __call__(self, result, *args, **kwargs):
        if result.current_state.should_stop:
            return

        result.start(self)
        self._timer = measure_time()
        try:
            res = super(Script, self).__call__(result, *args, **kwargs)
            result.add_success(self, self._timer())
            return res
        except BaseException as error:
            if self.__stop_if_error__:
                result.current_state.should_stop = True

            runnable.set_debug_if_allowed(self.config)
            result.add_error(self, traceback.format_exc(), self._timer(), error)


class BeforeScript(Script):

    __run_point__ = 'before'


class AfterScript(Script):

    __run_point__ = 'after'
