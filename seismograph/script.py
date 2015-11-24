# -*- coding: utf-8 -*-

from . import runnable


class Script(runnable.RunnableObject):

    __run_point__ = None
    __create_reason__ = False

    def __init__(self, program):
        super(Script, self).__init__()

        self.__program = program

    @property
    def config(self):
        return self.__program.config


class BeforeScript(Script):

    __run_point__ = 'before'


class AfterScript(Script):

    __run_point__ = 'after'
