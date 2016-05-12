# -*- coding: utf-8 -*-

import inspect

from seismograph import (
    case,
    suite,
    steps,
)
from seismograph.utils import pyv

from .lib.factories import (
    suite_factory,
)

from .lib.case import (
    BaseTestCase,
)
from .lib.layers import SuiteLayer


class TestSuiteContext(BaseTestCase):

    def setUp(self):
        self.base_layer = suite.SuiteLayer()
        self.suite_layer = SuiteLayer()
        self.suite = suite_factory.create()
        self.context = suite.SuiteContext(
            lambda: None,
            lambda: None,
        )
        self.context.add_layers([self.suite_layer])

    def tearDown(self):
        self.suite = None
        self.context = None
        self.base_layer = None
        self.suite_layer = None

    def test_on_init_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_init', None))

        signature = inspect.getargspec(self.base_layer.on_init)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.assertIsNotNone(getattr(self.context, 'on_init', None))

        signature = inspect.getargspec(self.context.on_init)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.context.on_init(self.suite)
        self.assertEqual(self.suite_layer.was_called, 'on_init')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_require_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_require', None))

        signature = inspect.getargspec(self.base_layer.on_require)
        self.assertEqual(signature.args, ['self', 'require'])

        self.assertIsNotNone(getattr(self.context, 'on_require', None))

        signature = inspect.getargspec(self.context.on_require)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.context.on_require(self.suite)
        self.assertEqual(self.suite_layer.was_called, 'on_require')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_build_rule_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_build_rule', None))

        signature = inspect.getargspec(self.base_layer.on_build_rule)
        self.assertEqual(signature.args, ['self', 'suite', 'rule'])

        self.assertIsNotNone(getattr(self.context, 'on_build_rule', None))

        signature = inspect.getargspec(self.context.on_build_rule)
        self.assertEqual(signature.args, ['self', 'suite', 'rule'])

        self.context.on_build_rule(self.suite, None)
        self.assertEqual(self.suite_layer.was_called, 'on_build_rule')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_setup_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_setup', None))

        signature = inspect.getargspec(self.base_layer.on_setup)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.assertIsNotNone(getattr(self.context, 'start_context', None))

        signature = inspect.getargspec(self.context.start_context)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.context.start_context(self.suite)
        self.assertEqual(self.suite_layer.was_called, 'on_setup')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_teardown_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_teardown', None))

        signature = inspect.getargspec(self.base_layer.on_teardown)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.assertIsNotNone(getattr(self.context, 'stop_context', None))

        signature = inspect.getargspec(self.context.stop_context)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.context.stop_context(self.suite)
        self.assertEqual(self.suite_layer.was_called, 'on_teardown')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_mount_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_mount', None))

        signature = inspect.getargspec(self.base_layer.on_mount)
        self.assertEqual(signature.args, ['self', 'suite', 'program'])

        self.assertIsNotNone(getattr(self.context, 'on_mount', None))

        signature = inspect.getargspec(self.context.on_mount)
        self.assertEqual(signature.args, ['self', 'suite', 'program'])

        self.context.on_mount(self.suite, None)
        self.assertEqual(self.suite_layer.was_called, 'on_mount')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_run_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_run', None))

        signature = inspect.getargspec(self.base_layer.on_run)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.assertIsNotNone(getattr(self.context, 'on_run', None))

        signature = inspect.getargspec(self.context.on_run)
        self.assertEqual(signature.args, ['self', 'suite'])

        self.context.on_run(self.suite)
        self.assertEqual(self.suite_layer.was_called, 'on_run')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_on_error_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_error', None))

        signature = inspect.getargspec(self.base_layer.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'suite', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_error', None))

        signature = inspect.getargspec(self.context.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'suite', 'result'])

        self.context.on_error(None, self.suite, None)
        self.assertEqual(self.suite_layer.was_called, 'on_error')
        self.assertEqual(self.suite_layer.counter, 1)

    def test_init_context(self):
        setup = lambda: None
        teardown = lambda: None

        context = suite.SuiteContext(setup, teardown)

        self.assertIn(setup, context.setup_callbacks)
        self.assertIn(teardown, context.teardown_callbacks)

        self.assertIsInstance(context.extensions, dict)


class TestSuiteObject(BaseTestCase):

    def test_init(self):
        layer = suite.SuiteLayer()
        suite_inst = suite.Suite(__name__, require=['hello'], layers=[layer])

        self.assertEqual(suite_inst.name, __name__)
        self.assertEqual(suite_inst.cases, [])
        self.assertIn(layer, suite_inst.context.layers)
        self.assertEqual(suite_inst.context.require, ['hello'])

        self.assertEqual(
            str(suite_inst),
            '<seismograph.suite.Suite method_name=run stopped_on=run>',
        )
        self.assertEqual(
            repr(suite_inst),
            '<seismograph.suite.Suite method_name=run stopped_on=run>',
        )

    def test_not_mount(self):
        suite_inst = suite.Suite(__name__)

        with self.assertRaises(AssertionError) as ctx:
            suite_inst.build()

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "build" of "seismograph.suite.Suite". Should be mount.',
        )

    def test_get_map(self):
        suite_inst = suite_factory.create()

        @suite_inst.register
        class CaseClass(case.Case):
            def test(self):
                pass

        @suite_inst.register
        class CaseClass2(case.Case):
            def test2(self):
                pass

        self.assertDictEqual(
            suite_inst.get_map(),
            {
                CaseClass.__name__: {
                    'tests': {
                        'test': CaseClass.test,
                    },
                    'cls': CaseClass,
                },
                CaseClass2.__name__: {
                    'tests': {
                        'test2': CaseClass2.test2,
                    },
                    'cls': CaseClass2,
                },
            }
        )


class TestRegisterCase(BaseTestCase):

    def test_basic(self):
        suite_inst = suite_factory.create()

        @suite_inst.register
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertIn(CaseClass, suite_inst.cases)

    def test_register_function(self):
        suite_inst = suite_factory.create()

        @suite_inst.register
        def function(tc):
            pass

        self.assertEqual(len(suite_inst.cases), 1)

        created_class = suite_inst.cases[0]
        self.assertTrue(type(created_class) == steps.CaseMeta)

        signature = inspect.getargspec(created_class.test)
        self.assertEqual(signature.args, ['tc'])

    def test_register_static_function(self):
        suite_inst = suite_factory.create()

        @suite_inst.register(static=True)
        def static_function():
            pass

        self.assertEqual(len(suite_inst.cases), 1)

        created_class = suite_inst.cases[0]
        self.assertTrue(type(created_class) == steps.CaseMeta)

        signature = inspect.getargspec(created_class.test)
        self.assertEqual(signature.args, ['s'])

    def test_flows_param(self):
        flows = (1, 2, 3, 4)
        suite_inst = suite_factory.create()

        @suite_inst.register(flows=flows)
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertEqual(CaseClass.__flows__, flows)

    def test_skip_param(self):
        suite_inst = suite_factory.create()

        @suite_inst.register(skip='some reason')
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertIsNotNone(getattr(CaseClass, case.SKIP_ATTRIBUTE_NAME, None))
        self.assertEqual(getattr(CaseClass, case.SKIP_WHY_ATTRIBUTE_NAME, None), 'some reason')

    def test_layers_param(self):
        layers = (case.CaseLayer(), )
        suite_inst = suite_factory.create()

        @suite_inst.register(layers=layers)
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertEqual(CaseClass.__layers__, layers)

    def test_set_layers_with_existed(self):
        layers = (case.CaseLayer(), )
        cls_layers = (case.CaseLayer(), )
        suite_inst = suite_factory.create()

        @suite_inst.register(layers=layers)
        class CaseClass(case.Case):

            __layers__ = cls_layers

            def test(self):
                pass

        self.assertEqual(CaseClass.__layers__, cls_layers + layers)

    def test_require_param(self):
        require = ['hello']
        suite_inst = suite_factory.create()

        @suite_inst.register(require=require)
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertEqual(CaseClass.__mount_data__.require, require)

    def test_assertion_class_param(self):
        suite_inst = suite_factory.create()

        class AssertionClass(case.AssertionBase):
            pass

        @suite_inst.register(assertion_class=AssertionClass)
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertEqual(CaseClass.__assertion_class__, AssertionClass)

    def test_case_class_param(self):
        suite_inst = suite_factory.create()

        class CaseClass(case.Case):
            pass

        @suite_inst.register(case_class=CaseClass)
        def function(tc):
            pass

        self.assertTrue(issubclass(function, CaseClass))
