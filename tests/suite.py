# -*- coding: utf-8 -*-

from seismograph import suite
from seismograph.utils import pyv

from .lib.case import (
    BaseTestCase,
)


class TestSuiteObject(BaseTestCase):

    def test_init(self):
        layer = suite.SuiteLayer()
        suite_inst = suite.Suite(__name__, require=['hello'], layers=[layer])

        self.assertEqual(suite_inst.name, __name__)
        self.assertEqual(suite_inst.cases, [])
        self.assertIn(layer, suite_inst.context.layers)
        self.assertEqual(suite_inst.context.require, ['hello'])

    def test_not_mount(self):
        suite_inst = suite.Suite(__name__)

        with self.assertRaises(AssertionError) as ctx:
            suite_inst.build()

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "build" of "seismograph.suite.Suite". Should be mount.',
        )
