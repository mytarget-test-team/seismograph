# -*- coding: utf-8 -*-

import inspect
from collections import OrderedDict

from seismograph import case
from seismograph import xunit
from seismograph import result
from seismograph.utils import pyv
from seismograph.steps import step
from seismograph import exceptions

from .factories import case_factory
from .factories import config_factory

from .lib.case import BaseTestCase
from .lib.case import RunCaseTestCaseMixin


class CaseLayer(case.CaseLayer):

    def __init__(self):
        super(CaseLayer, self).__init__()
        self.was_called = None
        self.counter = 0
        self.calling_story = []

    def on_init(self, case):
        self.was_called = 'on_init'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_require(self, require):
        self.was_called = 'on_require'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_setup(self, case):
        self.was_called = 'on_setup'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_teardown(self, case):
        self.was_called = 'on_teardown'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_skip(self, case, reason, result):
        self.was_called = 'on_skip'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_any_error(self, error, case, result):
        self.was_called = 'on_any_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_error(self, error, case, result):
        self.was_called = 'on_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_context_error(self, error, case, result):
        self.was_called = 'on_context_error'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_fail(self, fail, case, result):
        self.was_called = 'on_fail'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_success(self, case):
        self.was_called = 'on_success'
        self.counter += 1
        self.calling_story.append(self.was_called)

    def on_run(self, case):
        self.was_called = 'on_run'
        self.counter += 1
        self.calling_story.append(self.was_called)


class TestCaseContext(BaseTestCase):

    def setUp(self):
        self.base_layer = CaseLayer()
        self.empty_layer = CaseLayer()
        self.case = case_factory.create()
        self.context = case.CaseContext(
            lambda: None,
            lambda: None,
            layers=[self.empty_layer],
        )

    def tearDown(self):
        self.case = None
        self.context = None
        self.base_layer = None
        self.empty_layer = None

    def test_on_init_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_init', None))

        signature = inspect.getargspec(self.base_layer.on_init)
        self.assertEqual(signature.args, ['self', 'case'])

        self.assertIsNotNone(getattr(self.context, 'on_init', None))

        signature = inspect.getargspec(self.context.on_init)
        self.assertEqual(signature.args, ['self', 'case'])

        self.context.on_init(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_init')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_require_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_require', None))

        signature = inspect.getargspec(self.base_layer.on_require)
        self.assertEqual(signature.args, ['self', 'require'])

        self.assertIsNotNone(getattr(self.context, 'on_require', None))

        signature = inspect.getargspec(self.context.on_require)
        self.assertEqual(signature.args, ['self', 'case'])

        self.context.on_require(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_require')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_setup_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_setup', None))

        signature = inspect.getargspec(self.base_layer.on_setup)
        self.assertEqual(signature.args, ['self', 'case'])

        self.assertIsNotNone(getattr(self.context, 'start_context', None))

        self.context.start_context(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_setup')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_teardown_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_teardown', None))

        signature = inspect.getargspec(self.base_layer.on_teardown)
        self.assertEqual(signature.args, ['self', 'case'])

        self.assertIsNotNone(getattr(self.context, 'stop_context', None))

        self.context.stop_context(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_teardown')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_skip_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_skip', None))

        signature = inspect.getargspec(self.base_layer.on_skip)
        self.assertEqual(signature.args, ['self', 'case', 'reason', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_skip', None))

        signature = inspect.getargspec(self.context.on_skip)
        self.assertEqual(signature.args, ['self', 'case', 'reason', 'result'])

        self.context.on_skip(self.case, None, None)
        self.assertEqual(self.empty_layer.was_called, 'on_skip')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_any_error_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_any_error', None))

        signature = inspect.getargspec(self.base_layer.on_any_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_any_error', None))

        signature = inspect.getargspec(self.context.on_any_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.context.on_any_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_any_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_error_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_error', None))

        signature = inspect.getargspec(self.base_layer.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_error', None))

        signature = inspect.getargspec(self.context.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.context.on_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_context_error_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_context_error', None))

        signature = inspect.getargspec(self.base_layer.on_context_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_context_error', None))

        signature = inspect.getargspec(self.context.on_context_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])

        self.context.on_context_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_context_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_fail_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_fail', None))

        signature = inspect.getargspec(self.base_layer.on_fail)
        self.assertEqual(signature.args, ['self', 'fail', 'case', 'result'])

        self.assertIsNotNone(getattr(self.context, 'on_fail', None))

        signature = inspect.getargspec(self.context.on_fail)
        self.assertEqual(signature.args, ['self', 'fail', 'case', 'result'])

        self.context.on_fail(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_fail')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_success_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_success', None))

        signature = inspect.getargspec(self.base_layer.on_success)
        self.assertEqual(signature.args, ['self', 'case'])

        self.assertIsNotNone(getattr(self.context, 'on_success', None))

        signature = inspect.getargspec(self.context.on_success)
        self.assertEqual(signature.args, ['self', 'case'])

        self.context.on_success(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_success')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_run_callback(self):
        self.assertIsNotNone(getattr(self.base_layer, 'on_run', None))

        signature = inspect.getargspec(self.base_layer.on_run)
        self.assertEqual(signature.args, ['self', 'case'])

        self.assertIsNotNone(getattr(self.context, 'on_run', None))

        signature = inspect.getargspec(self.context.on_run)
        self.assertEqual(signature.args, ['self', 'case'])

        self.context.on_run(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_run')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_init_context(self):
        layer = CaseLayer()
        setup = lambda: None
        teardown = lambda: None

        context = case.CaseContext(setup, teardown, layers=[layer])

        self.assertIn(layer, context.layers)
        self.assertIn(setup, context.setup_callbacks)
        self.assertIn(teardown, context.teardown_callbacks)

        self.assertIsInstance(context.extensions, dict)


class TestAssertion(BaseTestCase):

    def test_unit_test(self):
        import unittest
        self.assertIsInstance(case.AssertionBase.__unittest__, unittest.TestCase)


class TestCaseObject(BaseTestCase):

    def test_not_mount(self):
        with self.assertRaises(AssertionError) as ctx:
            case.Case('__init__')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "__init__" of "seismograph.case.Case". Should be mount.',
        )

    def test_method_does_not_exist(self):
        with self.assertRaises(AttributeError) as ctx:
            case_factory.FakeCase('wow_wow')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            '"FakeCase" does not have attribute "wow_wow"',
        )

    def test_skip_method(self):
        case = case_factory.create()

        with self.assertRaises(AssertionError) as ctx:
            case.skip_test('reason')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "skip_test" of "tests.factories.case_factory.FakeCase". Should be run.',
        )

        with self.assertRaises(exceptions.Skip) as ctx:
            case_factory.mark_is_run(case)
            case.skip_test('reason')

        self.assertEqual(pyv.get_exc_message(ctx.exception), 'reason')

    def test_extension_not_required(self):
        case = case_factory.create()

        with self.assertRaises(exceptions.ExtensionNotRequired) as ctx:
            case.ext('hello')

        self.assertEqual(pyv.get_exc_message(ctx.exception), 'hello')

    def test_ext(self):
        case = case_factory.create()
        case.context.require.append('hello')
        case.context.extensions['hello'] = 'world'

        self.assertEqual(case.ext('hello'), 'world')

    def test_default_class_params(self):
        self.assertEqual(case.Case.__flows__, None)
        self.assertEqual(case.Case.__layers__, None)
        self.assertEqual(case.Case.__static__, False)
        self.assertEqual(case.Case.__require__, None)
        self.assertEqual(case.Case.__repeatable__, True)
        self.assertEqual(case.Case.__create_reason__, True)
        self.assertEqual(case.Case.__always_success__, False)
        self.assertEqual(case.Case.__assertion_class__, None)

    def test_init_assertion(self):
        case_inst = case_factory.create()
        self.assertIsInstance(case_inst.assertion, case.AssertionBase)

    def test_change_assertion_class(self):
        class TAssertion(case.AssertionBase):
            pass

        class TCase(case_factory.FakeCase):
            __assertion_class__ = TAssertion

        case_inst = TCase('__init__')
        self.assertIsInstance(case_inst.assertion, TAssertion)

    def test_reason_storage(self):
        case = case_factory.create()
        self.assertIsInstance(case.reason_storage, OrderedDict)

    def test_create_reason_for_simple_case(self):
        case = case_factory.create()
        reason = case.__reason__()
        self.assertEqual(reason, '')

        case.reason_storage['hello'] = 'world'
        reason = case.__reason__()
        self.assertEqual(reason, 'Case (info from test case): \n  hello: world\n\n')

    def test_create_reason_for_step_by_step_case(self):
        expected_reason = u'History (was done earlier): \n' \
                          u'  1. one step\n\n' \
                          u'Current step (when exception was raised): \n' \
                          u'  <StepByStepCase.one_step(1): one step>\n\n' \
                          u'Current flow (context of steps execution): \n' \
                          u'  Without flows\n\n'

        expected_reason_from_storage = 'Case (info from test case): \n  hello: world\n\n'

        class StepByStepCase(case_factory.FakeCase):
            @step(1, 'one step')
            def one_step(self):
                pass

        case = StepByStepCase('test', config=config_factory.create())
        case.test()

        reason = case.__reason__()
        self.assertEqual(reason, expected_reason)

        case.reason_storage['hello'] = 'world'
        reason = case.__reason__()
        self.assertEqual(
            reason,
            expected_reason + expected_reason_from_storage,
        )

    def test_class_name(self):
        case = case_factory.create()
        self.assertEqual(
            case.__class_name__(),
            'tests.factories.case_factory.FakeCase',
        )

    def test_method_name(self):
        case = case_factory.create()
        self.assertEqual(case.__method_name__(), 'test')

    def test_str_method(self):
        case = case_factory.create()
        self.assertEqual(
            case.__str__(),
            'test (tests.factories.case_factory:FakeCase)',
        )

    def test_repr_method(self):
        case = case_factory.create()
        self.assertEqual(
            case.__repr__(),
            '<tests.factories.case_factory:FakeCase method_name=test stopped_on=test>',
        )

    def test_init_context(self):
        case_inst = case_factory.create()
        self.assertIsInstance(case_inst.context, case.CaseContext)


class TestMakeCaseClassFromFunction(BaseTestCase):

    def setUp(self):
        def test_function(case):
            pass

        def static_case_function():
            pass

        self.test_function = test_function
        self.static_case_function = static_case_function

    def test_basic(self):
        class_from_func = case.make_case_class_from_function(
            self.test_function, case.Case,
        )
        self.assertTrue(issubclass(class_from_func, case.Case))
        self.assertEqual(class_from_func.__name__, 'test_function')

        signature = inspect.getargspec(class_from_func.test)
        self.assertEqual(signature.args, ['case'])

    def test_static_flag(self):
        class_from_func = case.make_case_class_from_function(
            self.static_case_function, case.Case,
            static=True,
        )
        self.assertTrue(issubclass(class_from_func, case.Case))
        self.assertEqual(class_from_func.__name__, 'static_case_function')

        signature = inspect.getargspec(class_from_func.test)
        self.assertEqual(signature.args, ['s'])

    def test_doc(self):
        class_from_func = case.make_case_class_from_function(
            self.test_function, case.Case,
            doc='It is doc string',
        )
        self.assertEqual(class_from_func.__doc__, 'It is doc string')

    def test_class_name(self):
        class_from_func = case.make_case_class_from_function(
            self.test_function, case.Case,
            class_name='NameForCaseClass',
        )
        self.assertTrue(issubclass(class_from_func, case.Case))
        self.assertEqual(class_from_func.__name__, 'NameForCaseClass')

    def test_class_name_creator(self):
        class_from_func = case.make_case_class_from_function(
            self.test_function, case.Case,
            class_name_creator=lambda f: 'la_la_la',
        )
        self.assertEqual(class_from_func.__name__, 'la_la_la')


class TestFlows(BaseTestCase):

    def test_flows_decorator_for_method(self):
        class TCClass(case_factory.FakeCase):
            counter = 0
            @case.flows(1, 2, 3, 4, 5)
            def test(self, i):
                self.counter += i

        case_inst = TCClass('test', config=config_factory.create())
        case_inst.test()

        self.assertEqual(case_inst.counter, 15)

    def test_flows_decorator_for_class(self):
        @case.flows(1, 2, 3, 4, 5)
        class TCClass(case_factory.FakeCase):
            counter = 0
            def test(self, i):
                self.counter += i

        self.assertEqual(TCClass.__flows__, (1, 2, 3, 4, 5))

        case_inst = TCClass('test', config=config_factory.create())
        case_inst.test()

        self.assertEqual(case_inst.counter, 15)

    def test_flows_class_param(self):
        class TCClass(case_factory.FakeCase):
            __flows__ = (1, 2, 3, 4, 5)
            counter = 0
            def test(self, i):
                self.counter += i

        case_inst = TCClass('test', config=config_factory.create())
        case_inst.test()

        self.assertEqual(case_inst.counter, 15)


class TestBasicRunCase(RunCaseTestCaseMixin, BaseTestCase):

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertFalse(self.result.errors)
        self.assertFalse(self.result.failures)
        self.assertEqual(len(self.result.successes), 1)
        self.assertEqual(self.result.current_state.tests, 1)
        self.assertIsInstance(self.case.log, result.Console.ChildConsole)


class TestFailCase(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        def test(self):
            raise AssertionError('no message')

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.failures), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.failures[0]
        self.assertIsInstance(case, self.CaseClass)
        self.assertIsInstance(reason, xunit.XUnitData)

        self.assertEqual(self.case.layer.counter, 6)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_fail', 'on_teardown'],
        )


class TestErrorCase(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        def test(self):
            raise Exception('no message')

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.errors[0]
        self.assertIsInstance(case, self.CaseClass)
        self.assertIsInstance(reason, xunit.XUnitData)

        self.assertEqual(self.case.layer.counter, 7)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_error', 'on_any_error', 'on_teardown'],
        )


class TestSkipCase(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        @case.skip('reason')
        def test(self):
            pass

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.skipped), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.skipped[0]
        self.assertIsInstance(case, self.CaseClass)
        self.assertIsInstance(reason, xunit.XUnitData)

        self.assertEqual(self.case.layer.counter, 6)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_skip', 'on_teardown'],
        )


class TestSkipIfCase(TestSkipCase):

    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        @case.skip_if(True, 'reason')
        def test(self):
            pass


class TestSkipUnlessCase(TestSkipCase):

    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        @case.skip_unless(False, 'reason')
        def test(self):
            pass


class TestSkipClass(RunCaseTestCaseMixin, BaseTestCase):

    @case.skip('reason')
    class CaseClass(case_factory.FakeCase):

        layer = CaseLayer()

        __layers__ = (layer, )

        def test(self):
            pass

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.skipped), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.skipped[0]
        self.assertIsInstance(case, self.CaseClass)
        self.assertIsInstance(reason, xunit.XUnitData)

        self.assertEqual(self.case.layer.counter, 3)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_skip'],
        )


class TestCaseCallbacks(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        calling_story = []

        @classmethod
        def setup_class(cls):
            cls.calling_story.append('setup_class')

        @classmethod
        def teardown_class(cls):
            cls.calling_story.append('teardown_class')

        def setup(self):
            self.calling_story.append('setup')

        def teardown(self):
            self.calling_story.append('teardown')

        def test(self):
            pass

    def make_case(self):
        super(TestCaseCallbacks, self).make_case()
        self.case = case.CaseBox([self.case])

    def runTest(self):
        self.assertEqual(
            self.case.calling_story,
            ['setup_class', 'setup', 'teardown', 'teardown_class'],
        )


class TestMountData(BaseTestCase):

    def runTest(self):
        mount_data = case.MountData('hello', ['world'])

        self.assertEqual(mount_data.suite_name, 'hello')
        self.assertEqual(mount_data.require, ['world'])


class TestRepeat(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        counter = 0

        def __repeat__(self):
            for _ in pyv.xrange(5):
                yield

        def test(self):
            self.counter += 1

    def runTest(self):
        self.assertEqual(self.case.counter, 5)


class TestRepeatMethod(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        counter = 0

        def __repeat_method__(self):
            for _ in pyv.xrange(5):
                yield

        def test(self):
            self.counter += 1

    def runTest(self):
        self.assertEqual(self.case.counter, 5)


class TestStepByStepCase(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        calling_story = []

        def begin(self):
            self.calling_story.append('begin')

        @step(1, 'step one')
        def step_one(self):
            self.calling_story.append('step_one')

        @step(2, 'step two')
        def step_two(self):
            self.calling_story.append('step_two')

        def finish(self):
            self.calling_story.append('finish')

    def runTest(self):
        self.assertEqual(
            self.case.__step_by_step__,
            True,
        )
        self.assertEqual(
            self.case.calling_story,
            ['begin', 'step_one', 'step_two', 'finish'],
        )
        self.assertEqual(
            self.case.__history__,
            [u'1. step one', u'2. step two'],
        )
        self.assertEqual(
            self.case.__current_step__,
            'finish',
        )
        self.assertEqual(
            len(self.case.__step_methods__),
            2,
        )


class TestFLowsOnStepByStepCase(RunCaseTestCaseMixin, BaseTestCase):

    class CaseClass(case_factory.FakeCase):

        __flows__ = (1, 2, 3, 4, 5)

        flows_sum = 0

        def begin(self, i):
            self.flows_sum += i

        @step(1, 'step one')
        def step_one(self, i):
            self.flows_sum += i

        def finish(self, i):
            self.flows_sum += i

    def runTest(self):
        self.assertEqual(self.case.flows_sum, 45)
