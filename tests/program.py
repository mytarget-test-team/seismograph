# -*- coding: utf-8 -*-

import inspect

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import seismograph
from seismograph import case
from seismograph import suite
from seismograph import config
from seismograph import result
from seismograph import script
from seismograph import program
from seismograph.utils import pyv
from seismograph import extensions

from .lib.case import (
    BaseTestCase,
)
from .lib.factories import (
    config_factory,
    program_factory,
)
from .lib import layers


class TestProgramContext(BaseTestCase):

    def setUp(self):
        self.base_layer = seismograph.ProgramLayer()
        self.program_layer = layers.ProgramLayer()
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
        self.assertEqual(signature.args, ['self', 'error', 'program', 'result', 'tb', 'timer'])

        self.assertIsNotNone(getattr(self.context, 'on_error', None))

        signature = inspect.getargspec(self.context.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'program', 'result', 'tb', 'timer'])

        self.context.on_error(None, self.program, None, None, None)
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

    def test_register_suite(self):
        program_inst = program.Program()

        suite_inst = suite.Suite('test')
        program_inst.register_suite(suite_inst)

        self.assertIn(suite_inst, program_inst.suites)

    def test_register_suites(self):
        program_inst = program.Program()

        suite_inst = suite.Suite('test')
        program_inst.register_suites([suite_inst])

        self.assertIn(suite_inst, program_inst.suites)

    def test_register_script(self):
        program_inst = program.Program()

        class Script(script.Script):

            def task(self):
                pass

        program_inst.register_script(Script)

        self.assertEqual(len(program_inst.scripts), 1)
        self.assertIsInstance(program_inst.scripts[0], Script)

    def test_register_scripts(self):
        program_inst = program.Program()

        class Script(script.Script):

            def task(self):
                pass

        program_inst.register_scripts([Script])

        self.assertEqual(len(program_inst.scripts), 1)
        self.assertIsInstance(program_inst.scripts[0], Script)

    def test_run_empty(self):
        program_inst = program.Program()

        with self.assertRaises(RuntimeError) as ctx:
            program_inst()

        self.assertEqual(pyv.get_exc_message(ctx.exception), 'No suites or scripts for execution')

    def test_require(self):
        program_inst = program.Program(require=['some_ext'])

        self.assertIn('some_ext', program_inst.context.require)


class TestSuiteIsValid(BaseTestCase):

    def test_basic(self):
        program_inst = program.Program()
        suite_inst = suite.Suite('package.module')

        self.assertTrue(program_inst.suite_is_valid(suite_inst))

    def test_include(self):
        config_inst = config_factory.create(INCLUDE_SUITES_PATTERN=r'^package.*$')
        program_inst = program_factory.create(config_inst)

        suite_one = suite.Suite('package.module')
        suite_two = suite.Suite('program.module')

        self.assertTrue(program_inst.suite_is_valid(suite_one))
        self.assertFalse(program_inst.suite_is_valid(suite_two))

    def test_exclude(self):
        config_inst = config_factory.create(EXCLUDE_SUITE_PATTERN=r'^program.*$')
        program_inst = program_factory.create(config_inst)

        suite_one = suite.Suite('package.module')
        suite_two = suite.Suite('program.module')

        self.assertTrue(program_inst.suite_is_valid(suite_one))
        self.assertFalse(program_inst.suite_is_valid(suite_two))


class TestShared(BaseTestCase):

    def test_shared_extension(self):
        ex_tmp = extensions._TMP

        try:
            class TestExtension(object):

                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs

            args = (1, 2, 3, 4, 5)
            kwargs = dict(a=1, b=2, c=3, d=4, e=5)

            program.Program.shared_extension(
                'test_extension',
                TestExtension,
                args=args,
                kwargs=kwargs,
            )

            self.assertIn('test_extension', ex_tmp)

            container = ex_tmp['test_extension']

            self.assertIsInstance(container, extensions.ExtensionContainer)
            self.assertFalse(isinstance(container, extensions.SingletonExtensionContainer))

            self.assertEqual(container.args, args)
            self.assertEqual(container.kwargs, kwargs)
            self.assertEqual(container.ext, TestExtension)
        finally:
            ex_tmp.pop('test_extension', None)

    def test_shared_singleton_extension(self):
        ex_tmp = extensions._TMP

        try:
            class TestExtension(object):

                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs

            args = (1, 2, 3, 4, 5)
            kwargs = dict(a=1, b=2, c=3, d=4, e=5)

            program.Program.shared_extension(
                'test_extension',
                TestExtension,
                args=args,
                kwargs=kwargs,
                singleton=True,
            )

            self.assertIn('test_extension', ex_tmp)

            container = ex_tmp['test_extension']

            self.assertIsInstance(container, extensions.SingletonExtensionContainer)

            self.assertEqual(container.args, args)
            self.assertEqual(container.kwargs, kwargs)
            self.assertEqual(container.ext, TestExtension)
        finally:
            ex_tmp.pop('test_extension', None)

    def test_shared_data(self):
        ex_tmp = extensions._TMP

        try:
            data = dict(a=1, b=2, c=3, d=4, e=5)
            program.Program.shared_data('test_data', data)

            self.assertIn('test_data', ex_tmp)
            self.assertEqual(ex_tmp['test_data'], data)
        finally:
            ex_tmp.pop('test_data', None)


class TestFullCycle(BaseTestCase):

    def runTest(self):
        case_layer = layers.CaseLayer()
        suite_layer = layers.SuiteLayer()
        program_layer = layers.ProgramLayer()

        suite_inst = suite.Suite('test', layers=[suite_layer])

        @suite_inst.register(layers=[case_layer])
        class TestOne(case.Case):

            def test(self):
                pass

        @suite_inst.register
        def simple_test(case):
            pass

        program_inst = program.Program(exit=False, stream=StringIO(), layers=[program_layer])
        program_inst.register_suite(suite_inst)

        self.assertTrue(program_inst())
        self.assertEqual(
            program_inst._Program__stream.getvalue(),
            u'Seismograph is measuring:\n\n'
            u'..\n\n'
            u'---------------------------------------------------------------\n'
            u'tests=2 failures=0 errors=0 skipped=0 successes=2 runtime=0.001\n'
        )

        self.assertEqual(
            case_layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_teardown', 'on_success'],
        )
        self.assertEqual(
            suite_layer.calling_story,
            ['on_init', 'on_require', 'on_mount', 'on_run', 'on_setup', 'on_teardown'],
        )
        self.assertEqual(
            program_layer.calling_story,
            ['on_option_parser', 'on_config', 'on_init', 'on_run', 'on_setup', 'on_teardown'],
        )
