# -*- coding: utf-8 -*-

from ... import suite
from ... import layers
from .case import SeleniumCase
from .extension import EX_NAME


class SeleniumSuiteLayer(layers.SuiteLayer):

    def on_require(self, require):
        if EX_NAME not in require:
            require.append(EX_NAME)


class SeleniumSuite(suite.Suite):

    __case_class__ = SeleniumCase
    __layers__ = (SeleniumSuiteLayer(), )
