# -*- coding: utf-8 -*-

import unittest

import seismograph
from types import ModuleType
from seismograph.utils import pyv

from .lib.case import BaseTestCase


EXCLUDE_FROM_FACADE = (
    'VERSION',
)


def filter_func(name):
    if not name.startswith('_') and name not in EXCLUDE_FROM_FACADE:
        return type(getattr(seismograph, name)) != ModuleType
    return False


@unittest.skipIf(pyv.IS_PYTHON_3, 'for python 2 only')
class TestFacadeOfLib(BaseTestCase):

    def assertFacadeOfLib(self, facade):
        for item in facade:
            self.assertIn(item, seismograph.__all__)

        for item in seismograph.__all__:
            self.assertIn(item, facade)

    @staticmethod
    def assertImportAll():
        try:
            from seismograph import *
        except BaseException as error:
            raise AssertionError(
                '{}: {}'.format(
                    error.__class__.__name__,
                    pyv.get_exc_message(error)
                ),
            )

    def runTest(self):
        facade = filter(
            filter_func,
            dir(seismograph),
        )
        self.assertImportAll()
        self.assertFacadeOfLib(facade)
