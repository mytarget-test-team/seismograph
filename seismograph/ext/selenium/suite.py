# -*- coding: utf-8 -*-

from ... import suite
from .case import SeleniumCase
from .extension import EX_NAME


class SeleniumSuiteLayer(suite.SuiteLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)


class SeleniumSuite(suite.Suite):

    __case_class__ = SeleniumCase
    __layers__ = (SeleniumSuiteLayer(), )
