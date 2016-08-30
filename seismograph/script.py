# -*- coding: utf-8 -*-

import traceback

from . import runnable
from .utils.common import measure_time


class Script(runnable.RunnableObject):

    __run_point__ = None
    __stop_if_error__ = False
    __create_reason__ = False

    def __init__(self, program, method_name):
        self.__program = program
        self._method_name = method_name

        super(Script, self).__init__()

        self.__is_run = False
        self._stopped_on = method_name

    def __str__(self):
        return '{} ({}:{})'.format(
            self._method_name,
            self.__class__.__module__,
            self.__class__.__name__,
        )

    def __is_run__(self):
        return self.__is_run

    def __method_name__(self):
        return self._method_name

    @property
    def config(self):
        return self.__program.config

    @property
    def ext(self):
        return self.__program.ext

    def __run__(self, result):
        self.__is_run = True

        if result.current_state.should_stop:
            return

        result.start(self)
        timer = measure_time()
        try:
            task = getattr(self, self._method_name)
            task()
            result.add_success(self, timer())
        except BaseException as error:
            if self.__stop_if_error__ or self.config.STOP:
                result.current_state.should_stop = True

            runnable.set_debug_if_allowed(self.config)
            result.add_error(self, traceback.format_exc(), timer(), error)


class BeforeScript(Script):

    __run_point__ = 'before'


class AfterScript(Script):

    __run_point__ = 'after'
