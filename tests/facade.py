# -*- coding: utf-8 -*-

import seismograph
from types import ModuleType

from .lib.case import BaseTestCase


EXCLUDE_FROM_FACADE = (
    'VERSION',
)


def get_facade():
    def filter_func(name):
        if not name.startswith('_') and name not in EXCLUDE_FROM_FACADE:
            return type(getattr(seismograph, name)) != ModuleType
        return False

    return list(filter(
        filter_func,
        dir(seismograph),
    ))


class TestFacadeOfLib(BaseTestCase):

    def assertFacadeOfLib(self, facade):
        for item in facade:
            self.assertIn(item, seismograph.__all__)

        for item in seismograph.__all__:
            self.assertIn(item, facade)

    @staticmethod
    def assertImportAll():
        from seismograph import __all__ as all

        for import_name in all:
            if getattr(seismograph, import_name, None) is None:
                raise AssertionError('Incorrect import name in "__all__"')

    def runTest(self):
        facade = get_facade()
        self.assertImportAll()
        self.assertFacadeOfLib(facade)
