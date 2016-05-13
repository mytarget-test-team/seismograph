# -*- coding: utf-8 -*-

import inspect

from seismograph import suite
from seismograph import config
from seismograph import result
from seismograph import program

from .lib.case import (
    BaseTestCase,
)
from .lib.layers import ProgramLayer


class TestProgramContext(BaseTestCase):

    def setUp(self):
        self.base_layer = program.ProgramLayer()
        self.program_layer = ProgramLayer()
        self.program = program.Program()
        self.context = program.ProgramContext(
            lambda: None,
            lambda: None,
        )
        self.context.add_layers([self.program_layer])

    def tearDown(self):
        self.program = None
        self.context = None
        self.base_layer = None
        self.program_layer = None

    def test_on_init_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_init', None))

        signature = inspect.getargspec(self.base_layer.on_init)
        self.assertEqual(signature.args, ['self', 'program'])

        self.assertIsNotNone(getattr(self.context, 'on_init', None))

        signature = inspect.getargspec(self.context.on_init)
        self.assertEqual(signature.args, ['self', 'program'])

        self.context.on_init(self.program)
        self.assertEqual(self.program_layer.was_called, 'on_init')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_config_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_config', None))

        signature = inspect.getargspec(self.base_layer.on_config)
        self.assertEqual(signature.args, ['self', 'config'])

        self.assertIsNotNone(getattr(self.context, 'on_config', None))

        signature = inspect.getargspec(self.context.on_config)
        self.assertEqual(signature.args, ['self', 'program', 'config'])

        self.context.on_config(self.program, None)
        self.assertEqual(self.program_layer.was_called, 'on_config')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_setup_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_setup', None))

        signature = inspect.getargspec(self.base_layer.on_setup)
        self.assertEqual(signature.args, ['self', 'program'])

        self.assertIsNotNone(getattr(self.context, 'start_context', None))

        signature = inspect.getargspec(self.context.start_context)
        self.assertEqual(signature.args, ['self', 'program'])

        self.context.start_context(self.program)
        self.assertEqual(self.program_layer.was_called, 'on_setup')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_teardown_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_teardown', None))

        signature = inspect.getargspec(self.base_layer.on_teardown)
        self.assertEqual(signature.args, ['self', 'program'])

        self.assertIsNotNone(getattr(self.context, 'stop_context', None))

        signature = inspect.getargspec(self.context.stop_context)
        self.assertEqual(signature.args, ['self', 'program'])

        self.context.stop_context(self.program)
        self.assertEqual(self.program_layer.was_called, 'on_teardown')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_error_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_error', None))

        signature = inspect.getargspec(self.base_layer.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'program', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_error', None))

        signature = inspect.getargspec(self.context.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'program', 'result'])

        self.context.on_error(None, self.program, None)
        self.assertEqual(self.program_layer.was_called, 'on_error')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_option_parser_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_option_parser', None))

        signature = inspect.getargspec(self.base_layer.on_option_parser)
        self.assertEqual(signature.args, ['self', 'parser'])

        self.assertIsNotNone(getattr(self.context, 'on_option_parser', None))

        signature = inspect.getargspec(self.context.on_option_parser)
        self.assertEqual(signature.args, ['self', 'parser'])

        self.context.on_option_parser(None)
        self.assertEqual(self.program_layer.was_called, 'on_option_parser')
        self.assertEqual(self.program_layer.counter, 1)

    def test_on_run_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_run', None))

        signature = inspect.getargspec(self.base_layer.on_run)
        self.assertEqual(signature.args, ['self', 'program'])

        self.assertIsNotNone(getattr(self.context, 'on_run', None))

        signature = inspect.getargspec(self.context.on_run)
        self.assertEqual(signature.args, ['self', 'program'])

        self.context.on_run(self.program)
        self.assertEqual(self.program_layer.was_called, 'on_run')
        self.assertEqual(self.program_layer.counter, 1)


class TestProgramObject(BaseTestCase):

    def test_init(self):
        program_inst = program.Program()

        self.assertEqual(program_inst.exit, True)
        self.assertEqual(program_inst.suites, [])
        self.assertEqual(program_inst.scripts, [])
        self.assertEqual(program_inst.suites_path, '__main__')
        self.assertIsInstance(program_inst.config, config.Config)
        self.assertIsInstance(program_inst.context, program.ProgramContext)

    def test_default_class_prams(self):
        self.assertEqual(program.Program.__layers__, None)
        self.assertEqual(program.Program.__suite_class__, suite.Suite)
        self.assertEqual(program.Program.__create_reason__, False)
        self.assertEqual(program.Program.__result_class__, result.Result)
        self.assertEqual(program.Program.__suite_group_class__, None)
        self.assertEqual(program.Program.__config_class__, config.Config)
