# -*- coding: utf-8 -*-

import seismograph
from types import ModuleType

from .lib.case import BaseTestCase


class TestFacadeOfLib(BaseTestCase):

    EXCLUDE_FROM_FACADE = (
        'VERSION',
    )

    def runTest(self):
        facade = filter(lambda a: not a.startswith('_'), dir(seismograph))
        for item in facade:
            if item not in self.EXCLUDE_FROM_FACADE \
                    and type(getattr(seismograph, item)) != ModuleType:
                self.assertIn(item, seismograph.__all__)

        for item in seismograph.__all__:
            self.assertIn(item, facade)
