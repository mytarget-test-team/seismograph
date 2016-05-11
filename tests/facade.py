# -*- coding: utf-8 -*-

import seismograph
from types import ModuleType

from .lib.case import BaseTestCase


EXCLUDE_FROM_FACADE = (
    'VERSION',
)


def filter_func(name):
    if not name.startswith('_') and name not in EXCLUDE_FROM_FACADE:
        return type(getattr(seismograph, name)) != ModuleType
    return False


class TestFacadeOfLib(BaseTestCase):

    def assertFacadeOfLib(self, facade):
        for item in facade:
            self.assertIn(item, seismograph.__all__)

        for item in seismograph.__all__:
            self.assertIn(item, facade)

    def runTest(self):
        facade = filter(
            filter_func,
            dir(seismograph),
        )
        self.assertFacadeOfLib(facade)
