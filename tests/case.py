# -*- coding: utf-8 -*-

import inspect
import unittest
from StringIO import StringIO
from collections import OrderedDict

from seismograph.case import (
    Case,
    CaseBox,
    flows,
    skip,
    skip_if,
    skip_unless,
    MountData,
    CaseLayer,
    CaseContext,
    AssertionBase,
    make_case_class_from_function,
)
from seismograph.exceptions import (
    Skip,
    ExtensionNotRequired,
)
from seismograph.utils import pyv
from seismograph.steps import step
from seismograph.result import (
    Result,
    Console,
)
from seismograph.xunit import XUnitData


def mark_is_run(case):
    case.__is_run__ = lambda: True


def create_empty_case(*args, **kwargs):
    return EmptyCase('test', *args, **kwargs)


class EmptyCase(Case):

    __mount_data__ = MountData('suite')

    def test(self):
        pass


class EmptyLayer(CaseLayer):

    def __init__(self):
        super(EmptyLayer, self).__init__()
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


class RunTestCaseMixin(object):

    class TCClass(EmptyCase):
        pass

    class FakeConfig(object):
        STOP = False
        REPEAT = False
        GEVENT = False
        VERBOSE = False
        NO_COLOR = True
        STEPS_LOG = False
        STEP_BY_STEP = False
        MULTIPROCESSING = False

    def setUp(self):
        self.create_case()
        self.stream = StringIO()
        self.result = Result(
            self.FakeConfig(),
            stream=self.stream,
        )
        self.run_case()

    def tearDown(self):
        self.case = None
        self.stream = None
        self.result = None

    def create_case(self):
        self.case = self.TCClass('test', config=self.FakeConfig())

    def run_case(self):
        self.case(self.result)


class TestCaseContext(unittest.TestCase):

    def setUp(self):
        self.base_layer = CaseLayer()
        self.empty_layer = EmptyLayer()
        self.case = create_empty_case()
        self.context = CaseContext(
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
        self.assertTrue(hasattr(self.base_layer, 'on_init'))

        signature = inspect.getargspec(self.base_layer.on_init)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_init'))

        signature = inspect.getargspec(self.context.on_init)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_init(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_init')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_require_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_require'))

        signature = inspect.getargspec(self.base_layer.on_require)
        self.assertEqual(signature.args, ['self', 'require'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_require'))

        signature = inspect.getargspec(self.context.on_require)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_require(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_require')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_setup_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_setup'))

        signature = inspect.getargspec(self.base_layer.on_setup)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'start_context'))

        self.context.start_context(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_setup')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_teardown_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_teardown'))

        signature = inspect.getargspec(self.base_layer.on_teardown)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'stop_context'))

        self.context.stop_context(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_teardown')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_skip_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_skip'))

        signature = inspect.getargspec(self.base_layer.on_skip)
        self.assertEqual(signature.args, ['self', 'case', 'reason', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_skip'))

        signature = inspect.getargspec(self.context.on_skip)
        self.assertEqual(signature.args, ['self', 'case', 'reason', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_skip(self.case, None, None)
        self.assertEqual(self.empty_layer.was_called, 'on_skip')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_any_error_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_any_error'))

        signature = inspect.getargspec(self.base_layer.on_any_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_any_error'))

        signature = inspect.getargspec(self.context.on_any_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_any_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_any_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_error_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_error'))

        signature = inspect.getargspec(self.base_layer.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_error'))

        signature = inspect.getargspec(self.context.on_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_context_error_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_context_error'))

        signature = inspect.getargspec(self.base_layer.on_context_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_context_error'))

        signature = inspect.getargspec(self.context.on_context_error)
        self.assertEqual(signature.args, ['self', 'error', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_context_error(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_context_error')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_fail_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_fail'))

        signature = inspect.getargspec(self.base_layer.on_fail)
        self.assertEqual(signature.args, ['self', 'fail', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_fail'))

        signature = inspect.getargspec(self.context.on_fail)
        self.assertEqual(signature.args, ['self', 'fail', 'case', 'result'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_fail(None, self.case, None)
        self.assertEqual(self.empty_layer.was_called, 'on_fail')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_success_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_success'))

        signature = inspect.getargspec(self.base_layer.on_success)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_success'))

        signature = inspect.getargspec(self.context.on_success)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_success(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_success')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_on_run_callback(self):
        self.assertTrue(hasattr(self.base_layer, 'on_run'))

        signature = inspect.getargspec(self.base_layer.on_run)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.assertTrue(hasattr(self.context, 'on_run'))

        signature = inspect.getargspec(self.context.on_run)
        self.assertEqual(signature.args, ['self', 'case'])
        self.assertEqual(signature.varargs, None)
        self.assertEqual(signature.keywords, None)
        self.assertEqual(signature.defaults, None)

        self.context.on_run(self.case)
        self.assertEqual(self.empty_layer.was_called, 'on_run')
        self.assertEqual(self.empty_layer.counter, 1)

    def test_init_context(self):
        layer = CaseLayer()
        setup = lambda: None
        teardown = lambda: None

        context = CaseContext(setup, teardown, layers=[layer])

        self.assertIn(layer, context.layers)
        self.assertIn(setup, context.setup_callbacks)
        self.assertIn(teardown, context.teardown_callbacks)

        self.assertIsInstance(context.extensions, dict)


class TestAssertion(unittest.TestCase):

    def test_unit_test(self):
        self.assertIsInstance(AssertionBase.__unittest__, unittest.TestCase)


class TestCaseObject(unittest.TestCase):

    def test_not_mount(self):
        with self.assertRaises(AssertionError) as ctx:
            Case('__init__')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "__init__" of "seismograph.case.Case". Should be mount.',
        )

    def test_method_does_not_exist(self):
        with self.assertRaises(AttributeError) as ctx:
            EmptyCase('wow_wow')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            '"EmptyCase" does not have attribute "wow_wow"',
        )

    def test_skip_method(self):
        case = create_empty_case()

        with self.assertRaises(AssertionError) as ctx:
            case.skip_test('reason')

        self.assertEqual(
            pyv.get_exc_message(ctx.exception),
            'Can not call "skip_test" of "tests.case.EmptyCase". Should be run.',
        )

        with self.assertRaises(Skip) as ctx:
            mark_is_run(case)
            case.skip_test('reason')

        self.assertEqual(pyv.get_exc_message(ctx.exception), 'reason')

    def test_extension_not_required(self):
        case = create_empty_case()

        with self.assertRaises(ExtensionNotRequired) as ctx:
            case.ext('hello')

        self.assertEqual(pyv.get_exc_message(ctx.exception), 'hello')

    def test_ext(self):
        case = create_empty_case()
        case.context.require.append('hello')
        case.context.extensions['hello'] = 'world'

        self.assertEqual(case.ext('hello'), 'world')

    def test_default_class_params(self):
        self.assertEqual(Case.__flows__, None)
        self.assertEqual(Case.__layers__, None)
        self.assertEqual(Case.__static__, False)
        self.assertEqual(Case.__require__, None)
        self.assertEqual(Case.__repeatable__, True)
        self.assertEqual(Case.__create_reason__, True)
        self.assertEqual(Case.__always_success__, False)
        self.assertEqual(Case.__assertion_class__, None)

    def test_init_assertion(self):
        case = create_empty_case()
        self.assertIsInstance(case.assertion, AssertionBase)

    def test_change_assertion_class(self):
        class TAssertion(AssertionBase):
            pass

        class TCase(EmptyCase):
            __assertion_class__ = TAssertion

        case = TCase('__init__')
        self.assertIsInstance(case.assertion, TAssertion)

    def test_reason_storage(self):
        case = create_empty_case()
        self.assertIsInstance(case.reason_storage, OrderedDict)

    def test_create_reason_for_simple_case(self):
        case = create_empty_case()
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

        class StepByStepCase(EmptyCase):
            @step(1, 'one step')
            def one_step(self):
                pass

        class FakeConfig(object):
            STEPS_LOG = False
            STEP_BY_STEP = False

        case = StepByStepCase('test', config=FakeConfig())
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
        case = EmptyCase('test')
        self.assertEqual(case.__class_name__(), 'suite.EmptyCase')

    def test_method_name(self):
        case = EmptyCase('test')
        self.assertEqual(case.__method_name__(), 'test')

    def test_str_method(self):
        case = EmptyCase('test')
        self.assertEqual(case.__str__(), 'test (suite:EmptyCase)')

    def test_repr_method(self):
        case = EmptyCase('test')
        self.assertEqual(case.__repr__(), '<suite:EmptyCase method_name=test stopped_on=test>')

    def test_init_context(self):
        case = create_empty_case()
        self.assertIsInstance(case.context, CaseContext)


class TestMakeCaseClassFromFunction(unittest.TestCase):

    def setUp(self):
        def test_function(case):
            pass

        def static_case_function():
            pass

        self.test_function = test_function
        self.static_case_function = static_case_function

    def test_basic(self):
        class_from_func = make_case_class_from_function(
            self.test_function, Case,
        )
        self.assertTrue(issubclass(class_from_func, Case))
        self.assertEqual(class_from_func.__name__, 'test_function')

        signature = inspect.getargspec(class_from_func.test)
        self.assertEqual(signature.args, ['case'])

    def test_static_flag(self):
        class_from_func = make_case_class_from_function(
            self.static_case_function, Case,
            static=True,
        )
        self.assertTrue(issubclass(class_from_func, Case))
        self.assertEqual(class_from_func.__name__, 'static_case_function')

        signature = inspect.getargspec(class_from_func.test)
        self.assertEqual(signature.args, ['s'])

    def test_doc(self):
        class_from_func = make_case_class_from_function(
            self.test_function, Case,
            doc='It is doc string',
        )
        self.assertEqual(class_from_func.__doc__, 'It is doc string')

    def test_class_name(self):
        class_from_func = make_case_class_from_function(
            self.test_function, Case,
            class_name='NameForCaseClass',
        )
        self.assertTrue(issubclass(class_from_func, Case))
        self.assertEqual(class_from_func.__name__, 'NameForCaseClass')

    def test_class_name_creator(self):
        class_from_func = make_case_class_from_function(
            self.test_function, Case,
            class_name_creator=lambda f: 'la_la_la',
        )
        self.assertEqual(class_from_func.__name__, 'la_la_la')


class TestFlows(unittest.TestCase):

    class FakeConfig(object):
        FLOWS_LOG = False

    def test_flows_decorator_for_method(self):
        class TCClass(EmptyCase):
            counter = 0
            @flows(1, 2, 3, 4, 5)
            def test(self, i):
                self.counter += i

        case = TCClass('test', config=self.FakeConfig())
        case.test()

        self.assertEqual(case.counter, 15)

    def test_flows_decorator_for_class(self):
        @flows(1, 2, 3, 4, 5)
        class TCClass(EmptyCase):
            counter = 0
            def test(self, i):
                self.counter += i

        self.assertEqual(TCClass.__flows__, (1, 2, 3, 4, 5))

        case = TCClass('test', config=self.FakeConfig())
        case.test()

        self.assertEqual(case.counter, 15)

    def test_flows_class_param(self):
        class TCClass(EmptyCase):
            __flows__ = (1, 2, 3, 4, 5)
            counter = 0
            def test(self, i):
                self.counter += i

        case = TCClass('test', config=self.FakeConfig())
        case.test()

        self.assertEqual(case.counter, 15)


class TestBasicRunCase(RunTestCaseMixin, unittest.TestCase):

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertFalse(self.result.errors)
        self.assertFalse(self.result.failures)
        self.assertEqual(len(self.result.successes), 1)
        self.assertEqual(self.result.current_state.tests, 1)
        self.assertIsInstance(self.case.log, Console.ChildConsole)


class TestFailCase(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        def test(self):
            raise AssertionError('no message')

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.failures), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.failures[0]
        self.assertIsInstance(case, self.TCClass)
        self.assertIsInstance(reason, XUnitData)

        self.assertEqual(self.case.layer.counter, 6)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_fail', 'on_teardown'],
        )


class TestErrorCase(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        def test(self):
            raise Exception('no message')

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.errors[0]
        self.assertIsInstance(case, self.TCClass)
        self.assertIsInstance(reason, XUnitData)

        self.assertEqual(self.case.layer.counter, 7)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_error', 'on_any_error', 'on_teardown'],
        )


class TestSkipCase(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        @skip('reason')
        def test(self):
            pass

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.skipped), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.skipped[0]
        self.assertIsInstance(case, self.TCClass)
        self.assertIsInstance(reason, XUnitData)

        self.assertEqual(self.case.layer.counter, 6)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_run', 'on_setup', 'on_skip', 'on_teardown'],
        )


class TestSkipIfCase(TestSkipCase):

    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        @skip_if(True, 'reason')
        def test(self):
            pass


class TestSkipUnlessCase(TestSkipCase):

    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        @skip_unless(False, 'reason')
        def test(self):
            pass


class TestSkipClass(RunTestCaseMixin, unittest.TestCase):

    @skip('reason')
    class TCClass(EmptyCase):

        layer = EmptyLayer()

        __layers__ = (layer, )

        def test(self):
            pass

    def runTest(self):
        self.assertTrue(self.case.__is_run__())
        self.assertEqual(len(self.result.skipped), 1)
        self.assertEqual(self.result.current_state.tests, 1)

        case, reason = self.result.skipped[0]
        self.assertIsInstance(case, self.TCClass)
        self.assertIsInstance(reason, XUnitData)

        self.assertEqual(self.case.layer.counter, 3)
        self.assertEqual(
            self.case.layer.calling_story,
            ['on_init', 'on_require', 'on_skip'],
        )


class TestCaseCallbacks(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

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

    def create_case(self):
        super(TestCaseCallbacks, self).create_case()
        self.case = CaseBox([self.case])

    def runTest(self):
        self.assertEqual(
            self.case.calling_story,
            ['setup_class', 'setup', 'teardown', 'teardown_class'],
        )


class TestMountData(unittest.TestCase):

    def runTest(self):
        mount_data = MountData('hello', ['world'])

        self.assertEqual(mount_data.suite_name, 'hello')
        self.assertEqual(mount_data.require, ['world'])


class TestRepeat(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        counter = 0

        def __repeat__(self):
            for _ in pyv.xrange(5):
                yield

        def test(self):
            self.counter += 1

    def runTest(self):
        self.assertEqual(self.case.counter, 5)


class TestRepeatMethod(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        counter = 0

        def __repeat_method__(self):
            for _ in pyv.xrange(5):
                yield

        def test(self):
            self.counter += 1

    def runTest(self):
        self.assertEqual(self.case.counter, 5)


class TestStepByStepCase(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

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


class TestFLowsOnStepByStepCase(RunTestCaseMixin, unittest.TestCase):

    class TCClass(EmptyCase):

        __flows__ = (1, 2, 3, 4, 5)

        was_executed = []

        def begin(self, i):
            self.was_executed.append(i)

        @step(1, 'step one')
        def step_one(self, i):
            self.was_executed.append(i)

        def finish(self, i):
            self.was_executed.append(i)

    def runTest(self):
        self.assertEqual(
            self.case.was_executed,
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5],
        )
