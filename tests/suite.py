# -*- coding: utf-8 -*-

import inspect

from seismograph import (
    case,
    suite,
    steps,
)
from seismograph.utils import pyv

from .lib.factories import (
    case_factory,
    suite_factory,
    config_factory,
)

from .lib.case import (
    BaseTestCase,
    SuiteTestCaseMixin,
    ResultTestCaseMixin,
    RunSuiteTestCaseMixin,
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

    def test_assign_build_rule(self):
        suite_inst = suite.Suite(__name__)
        rule = suite.BuildRule(__name__, case_name='MyTestCase', test_name='test')

        suite_inst.assign_build_rule(rule)

        self.assertIn(rule, suite_inst.context.build_rules)

    def test_assign_incorrect_build_rule(self):
        suite_inst = suite.Suite(__name__)
        rule = suite.BuildRule('incorrect.name', case_name='MyTestCase')

        with self.assertRaises(AssertionError) as ctx:
            suite_inst.assign_build_rule(rule)

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Build rule "incorrect.name:MyTestCase" is not of this suite',
        )

    def test_create_reason(self):
        suite_inst = suite.Suite(__name__)
        suite_inst.reason_storage['hello'] = 'world'

        reason = suite_inst.__reason__()
        self.assertEqual(
            reason, 'Suite (info from suite): \n  hello: world\n\n',
        )

    def test_default_class_params(self):
        self.assertEqual(suite.Suite.__layers__, None)
        self.assertEqual(suite.Suite.__require__, None)
        self.assertEqual(suite.Suite.__create_reason__, True)
        self.assertEqual(suite.Suite.__case_class__, case.Case)
        self.assertEqual(suite.Suite.__case_group_class__, None)
        self.assertEqual(suite.Suite.__case_box_class__, case.CaseBox)


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

    def test_always_success_param(self):
        suite_inst = suite_factory.create()

        self.assertFalse(case.Case.__always_success__)

        @suite_inst.register(always_success=True)
        class CaseClass(case.Case):
            def test(self):
                pass

        self.assertTrue(CaseClass.__always_success__)


class TestBuildRule(BaseTestCase):

    def test_basic(self):
        rule = suite.BuildRule(
            'package.module',
            case_name='ClassName',
            test_name='method_name',
        )

        self.assertEqual(rule.suite_name, 'package.module')
        self.assertEqual(rule.case_name, 'ClassName')
        self.assertEqual(rule.test_name, 'method_name')

    def test_to_str(self):
        rule_1 = suite.BuildRule(
            'package.module',
            case_name='ClassName',
            test_name='method_name',
        )
        rule_2 = suite.BuildRule(
            'package.module',
            case_name='ClassName',
        )
        rule_3 = suite.BuildRule(
            'package.module',
        )

        self.assertEqual(str(rule_1), 'package.module:ClassName.method_name')
        self.assertEqual(str(rule_2), 'package.module:ClassName')
        self.assertEqual(str(rule_3), 'package.module')

    def test_repr(self):
        rule = suite.BuildRule(
            'package.module',
            case_name='ClassName',
            test_name='method_name',
        )

        self.assertEqual(
            repr(rule),
            '<BuildRule(suite_name=package.module, case_name=ClassName, test_name=method_name)>',
        )

    def test_is_of(self):
        suite_inst = suite.Suite(__name__)
        rule = suite.BuildRule(__name__)

        self.assertTrue(rule.is_of(suite_inst))

    def test_is_of_negative(self):
        suite_inst = suite.Suite(__name__)
        rule = suite.BuildRule('package.module')

        self.assertFalse(rule.is_of(suite_inst))


class TestMountData(BaseTestCase):

    def test_basic(self):
        config = config_factory.create()
        mount_data = suite.MountData(config)

        self.assertEqual(mount_data.config, config)


class TestRunSuite(RunSuiteTestCaseMixin, BaseTestCase):

    class SuiteClass(suite.Suite):

        layer = SuiteLayer()
        __layers__ = (layer, )

    def runTest(self):
        self.assertTrue(self.suite.__is_run__())
        self.assertEqual(len(self.result.successes), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        self.assertEqual(
            self.suite.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_teardown'],
        )


class TestCallbacksCall(RunSuiteTestCaseMixin, BaseTestCase):

    class SuiteClass(suite.Suite):

        calling_story = []

        def setup(self):
            self.calling_story.append('setup')

        def teardown(self):
            self.calling_story.append('teardown')

    def runTest(self):
        self.assertEqual(self.suite.calling_story, ['setup', 'teardown'])


class TestErrorOnContext(RunSuiteTestCaseMixin, BaseTestCase):

    class SuiteClass(suite.Suite):

        class LayerClass(SuiteLayer):

            def on_run(self, suite):
                raise Exception('message')

        layer = LayerClass()
        __layers__ = (layer, )

    def runTest(self):
        self.assertTrue(self.suite.__is_run__())
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        self.assertFalse(self.result.failures)
        self.assertFalse(self.result.successes)

        self.assertEqual(
            self.suite.layer.calling_story,
            ['on_init', 'on_require', 'on_error'],
        )


class TestShouldStop(SuiteTestCaseMixin, ResultTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        def test(self):
            pass

    def runTest(self):
        self.result.current_state.should_stop = True

        self.suite.cases.append(self.CaseClass)
        self.suite.build()
        self.suite(self.result)

        self.assertFalse(self.result.errors)
        self.assertFalse(self.result.failures)
        self.assertFalse(self.result.successes)
        self.assertEqual(self.result.current_state.tests, 0)
