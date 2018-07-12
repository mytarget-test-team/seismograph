# -*- coding: utf-8 -*-

import re
import logging
import traceback
from functools import wraps
from unittest import TestCase as __UnitTest__

from six import with_metaclass

from . import steps
from . import loader
from . import reason
from . import runnable
from .utils import pyv
from . import extensions
from .utils import common
from .exceptions import Skip
from .utils.common import measure_time
from .utils.common import call_to_chain
from .exceptions import DependencyError
from .exceptions import ExtensionNotRequired
from .exceptions import ALLOW_RAISED_EXCEPTIONS


logger = logging.getLogger(__name__)


DEFAULT_LAYERS = []
MATCH_CASE_TO_LAYER = {}


SKIP_ATTRIBUTE_NAME = '__skip__'
SKIP_WHY_ATTRIBUTE_NAME = '__skip_why__'


_jsonschema = None


def _import_json_schema():
    global _jsonschema

    try:
        import jsonschema
        _jsonschema = jsonschema
    except ImportError:
        raise DependencyError(
            'Dependence "jsonschema" is not found. Please install it and try again.',
        )


def repeat(case):
    return case.__repeat__()


def repeat_method(case):
    return case.__repeat_method__()


def prepare(case, method):
    return case.__prepare__(method)


def setup_class_proxy(case):
    if getattr(case.__class__, '__setup_class_was_called__', False):
        return
    case.setup_class()
    setattr(case.__class__, '__setup_class_was_called__', True)


def teardown_class_proxy(case):
    if getattr(case.__class__, '__teardown_class_was_called__', False):
        return
    case.teardown_class()
    setattr(case.__class__, '__teardown_class_was_called__', True)


def _skip(reason):
    def wrapper(case):
        if not pyv.is_class_type(case):
            @wraps(case)
            def wrapped(*args, **kwargs):
                raise Skip(reason)
            case = wrapped

        setattr(case, SKIP_ATTRIBUTE_NAME, True)
        setattr(case, SKIP_WHY_ATTRIBUTE_NAME, reason)

        return case
    return wrapper


def skip(reason):
    return _skip(reason)


def skip_if(condition, reason):
    if condition:
        return _skip(reason)
    return lambda obj: obj


def skip_unless(condition, reason):
    if not condition:
        return _skip(reason)
    return lambda obj: obj


def set_no_skip():
    global _skip

    def no_skip(reason):
        def wrapper(f):
            return f
        return wrapper

    _skip = no_skip


def flows(*flows):
    def wrapper(f):
        if pyv.is_class_type(f):
            setattr(f, '__flows__', flows)
            return f

        @wraps(f)
        def wrapped(self, *args, **kwargs):
            for flow in flows:
                if self.config.FLOWS_LOG:
                    with self.log.tab():
                        self.log(
                            'Flow: ', pyv.unicode_string(flow),
                        )
                f(self, flow, *args, **kwargs)
        return wrapped
    return wrapper


def apply_flows(case):
    if not steps.is_step_by_step_case(case) and case.__flows__:
        setattr(
            case.__class__,
            runnable.method_name(case),
            flows(*case.__flows__)(
                getattr(case.__class__, runnable.method_name(case)),
            ),
        )


def make_case_class_from_function(
        func,
        base_class,
        doc=None,
        static=False,
        class_name=None,
        class_name_creator=None):
    if callable(class_name_creator):
        class_name = class_name_creator(func)

    if static or base_class.__static__:
        method = lambda s, *a, **k: func(*a, **k)
    else:
        method = func

    cls = type(
        class_name or func.__name__,
        (base_class, ),
        {
            '__doc__': doc or func.__doc__,
            loader.DEFAULT_TEST_NAME: method,
        },
    )

    return cls


def with_match_layers(context, case):
    for layer in context.layers:
        yield layer

    for cls, layer in MATCH_CASE_TO_LAYER.items():
        if isinstance(case, cls) and layer.enabled:
            yield layer


class CaseBox(object):

    def __init__(self, iterable):
        self.__cases = iterable
        self.__current = None

        logger.debug('CaseBox was created')

    def __call__(self, *args, **kwargs):
        return self.__run__(*args, **kwargs)

    def __iter__(self):
        for case in self.__cases:
            yield case

    def __repr__(self):
        if self.__current:
            return repr(self.__current)
        return super(CaseBox, self).__repr__()

    def __str__(self):
        return str(self.__current)

    def __getattr__(self, item):
        return getattr(self.__current, item)

    def __len__(self):
        return len(self.__cases)

    def __run_current__(self, result):
        if self.__current.__repeatable__ and self.__current.config.REPEAT > 0:
            for _ in pyv.xrange(self.__current.config.REPEAT):
                self.__current(result)
        else:
            self.__current(result)

    def __run__(self, result):
        for case in self.__cases:
            self.__current = case
            try:
                setup_class_proxy(self.__current)
            except BaseException as error:
                runnable.stopped_on(self.__current, 'setup_class')
                raise error
            self.__run_current__(result)

        if self.__current:
            try:
                teardown_class_proxy(self.__current)
            except BaseException as error:
                runnable.stopped_on(self.__current, 'teardown_class')
                raise error


class MountData(object):

    def __init__(self, suite_name=None, require=None):
        self.__require = require
        self.__suite_name = suite_name

    @property
    def require(self):
        return self.__require

    @property
    def suite_name(self):
        return self.__suite_name


class AssertionBase(object):

    __unittest__ = __UnitTest__('__call__')

    def __json_schema_by_response__(self, resp):
        raise NotImplementedError(
            'You should implemented "__json_schema_by_response__" method in {}'.format(
                self.__class__.__name__,
            ),
        )

    def len_equal(self, a, b, msg=None):
        """
        Check equal from length of list or tuple

        len_equal([1, 2, 3], 3)
        """
        if type(b) == int:
            self.equal(len(a), b, msg=msg)
        else:
            self.equal(a, len(b), msg=msg)

    def fail(self, msg=None):
        """
        Raised AssertionError with message
        """
        self.__unittest__.fail(msg)

    def true(self, expr, msg=None):
        """
        Like assertTrue in unittest
        """
        self.__unittest__.assertTrue(expr, msg=msg)

    def false(self, expr, msg=None):
        """
        Like assertFalse in unittest
        """
        self.__unittest__.assertFalse(expr, msg=msg)

    def greater(self, a, b, msg=None):
        """
        Like assertGreater in unittest
        """
        self.__unittest__.assertGreater(a, b, msg=msg)

    def equal(self, first, second, msg=None):
        """
        Like assertEqual in unittest
        """
        self.__unittest__.assertEqual(first, second, msg=msg)

    def not_equal(self, first, second, msg=None):
        """
        Like assertNotEqual in unittest
        """
        self.__unittest__.assertNotEqual(first, second, msg=msg)

    def raises(self, *args, **kwargs):
        """
        Like assertRaises in unittest
        """
        return self.__unittest__.assertRaises(*args, **kwargs)

    def is_instance(self, obj, cls, msg=None):
        """
        Like assertIsInstance in unittest
        """
        self.__unittest__.assertIsInstance(obj, cls, msg=msg)

    def sequence_equal(self, seq1, seq2, msg=None, seq_type=None):
        """
        Like assertSequenceEqual in unittest
        """
        self.__unittest__.assertSequenceEqual(seq1, seq2, msg=msg, seq_type=seq_type)

    def almost_equal(self, first, second, places=None, msg=None, delta=None):
        """
        Like assertAlmostEqual in unittest
        """
        self.__unittest__.assertAlmostEqual(first, second, places=places, msg=msg, delta=delta)

    def not_almost_equal(self, first, second, places=None, msg=None, delta=None):
        """
        Like assertNotAlmostEqual in unittest
        """
        self.__unittest__.assertNotAlmostEqual(first, second, places=places, msg=msg, delta=delta)

    def is_in(self, member, container, msg=None):
        """
        Like assertIn in unittest
        """
        self.__unittest__.assertIn(member, container, msg=msg)

    def is_not_in(self, member, container, msg=None):
        """
        Like assertNotIn in unittest
        """
        self.__unittest__.assertNotIn(member, container, msg=msg)

    def is_none(self, obj, msg=None):
        """
        Like assertIsNone in unittest
        """
        self.__unittest__.assertIsNone(obj, msg=msg)

    def is_not_none(self, obj, msg=None):
        """
        Like assertIsNotNone in unittest
        """
        self.__unittest__.assertIsNotNone(obj, msg=msg)

    def equal_by_iter(self, seq1, seq2, msg=None):
        """
        Compare two iterable objects.

        Example::

            assertion.equal_by_iter(['hello', 'world'], set(['hello', 'world'])).
            assertion.equal_by_iter(dict(a=1, b=2), ('a', 'b))
        """
        compare_error = 'compare by iter: {} != {}'.format(seq1, seq2)
        len_error = 'discrepancy of objects length: {} != {}'.format(len(seq1), len(seq2))

        self.equal(len(seq1), len(seq2), msg=msg or len_error)

        for first, second in zip(seq1, seq2):
            self.equal(first, second, msg=msg or compare_error)

    def dict_equal(self, d1, d2, msg=None):
        """
        Like assertDictEqual in unittest
        """
        self.__unittest__.assertDictEqual(d1, d2, msg=msg)

    def _dates_format(self, date1, date2):
        from_date = lambda d: sum(sorted((d.year, d.month, d.day)))
        from_string = lambda d: sum(sorted(int(i) for i in re.findall(r'[0-9]+', d)))

        d1 = from_string(date1) if isinstance(date1, pyv.basestring) else from_date(date1)
        d2 = from_string(date2) if isinstance(date2, pyv.basestring) else from_date(date2)

        return d1, d2

    def dates_equal(self, date1, date2):
        """
        To compare dates. Date can be as string and date object.

        For example::

            import datetime
            dates_equal(datetime.date(2016, 8, 16), '16.08.2016')
        """
        dates = self._dates_format(date1, date2)
        if dates[0] != dates[1]:
            self.fail('{} != {}'.format(date1, date2))

    def dates_not_equal(self, date1, date2):
        """
        To compare dates. Date can be as string and date object.

        For example::

            import datetime
            dates_not_equal(datetime.date(2016, 8, 16), '16.08.2016')
        """
        dates = self._dates_format(date1, date2)
        if dates[0] == dates[1]:
            self.fail('{} = {}'.format(date1, date2))

    def response(self,
                 resp,
                 status,
                 data=None,
                 schema=None,
                 length=None,
                 required=None,
                 use_schema=True,
                 use_required=True):
        """
        Validate HTTP response from request lib.

        :param resp: validate http response
        :param status: compare with http response status
        :param data: compare with http response content
        :param schema: compare with http response content json schema
        :param length: compare with http response length
        :param required: compare with required field in http response
        :param use_schema: True or False
        :param use_required: True or False

        Example::

            AssertionBase().response(
                resp,
                200,
                data={'id': 100},
                required=['id', 'name'],
            )

        You should implemented "__json_schema_by_response__" magic method in "AssertionBase"
        and can use own strategy for obtaining json schema in depending of response.
        Or use hard schema in parameter 'schema', parameter 'schema' has higher priority
        than "__json_schema_by_response__" method.
        """
        if resp.status_code != status:
            raise AssertionError(
                'response status: {}, expected: {}'.format(
                    resp.status_code, status,
                ),
            )

        schema = schema or self.__json_schema_by_response__(resp) if use_schema else None

        if length is not None:
            self.len_equal(resp.json(), length)

        if data is None and schema is None:
            return

        resp_data = common.get_dict_from_list(
            resp.json(),
            **data if isinstance(data, dict) else {}
        )

        if schema:
            if _jsonschema is None:
                _import_json_schema()

            if required:
                schema = schema.copy()
                schema.update(required=required)
            elif not use_required:
                if 'required' in schema:
                    schema = schema.copy()
                    del schema['required']

            try:
                _jsonschema.validate(resp_data, schema)
            except _jsonschema.ValidationError as error:
                self.fail('\n\n' + pyv.unicode(error))
        elif required:
            if isinstance(resp_data, list):
                for resp_data_item in resp_data:
                    for field_name in required:
                        self.is_in(field_name, resp_data_item)
            elif isinstance(resp_data, dict):
                for field_name in required:
                    self.is_in(field_name, resp_data)

        if data:
            if isinstance(data, dict):
                self.is_instance(resp_data, dict, msg='response is not type of dict')
                self.dict_equal(common.reduce_dict(resp_data, data), data)

            elif isinstance(data, (list, tuple)):
                self.is_instance(resp_data, list, msg='response is not type of list')
                self.equal(
                    len(resp_data), len(data),
                    msg='objects of different lengths: {} != {}'.format(
                        len(resp_data), len(data),
                    ),
                )

                resp_data, data = common.reduce_list(resp_data, data)

                for item in resp_data:
                    index = resp_data.index(item)
                    if isinstance(item, dict):
                        self.dict_equal(item, data[index])
                    else:
                        self.equal(item, data[index])

            elif isinstance(data, pyv.basestring):
                self.is_instance(resp_data, pyv.basestring, msg='response is not type of string')
                self.equal(resp_data, data)

            else:
                raise TypeError('Incorrect type of data')


class CaseContext(runnable.ContextOfRunnableObject):

    def __init__(self,
                 setup,
                 teardown,
                 layers=None):
        self.__require = []
        self.__extensions = {}
        self.__layers = layers if layers else []

        self.__setup_callbacks = [setup]
        self.__teardown_callbacks = [teardown]

    @property
    def require(self):
        return self.__require

    @property
    def extensions(self):
        return self.__extensions

    @property
    def setup_callbacks(self):
        return self.__setup_callbacks

    @property
    def teardown_callbacks(self):
        return self.__teardown_callbacks

    @property
    def layers(self):
        for layer in self.__layers:
            if layer.enabled:
                yield layer

        for layer in DEFAULT_LAYERS:
            if layer.enabled:
                yield layer

    def start_context(self, case):
        logger.debug(
            'Start context of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_setup', case,
            )
            call_to_chain(self.__setup_callbacks, None)
        except BaseException:
            runnable.stopped_on(case, 'start_context')
            raise

    def stop_context(self, case):
        logger.debug(
            'Stop context of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_teardown', case,
            )
            call_to_chain(self.__teardown_callbacks, None)
        except BaseException:
            runnable.stopped_on(case, 'stop_context')
            raise

    def install_extensions(self):
        for ext_name in self.require:
            if ext_name not in self.__extensions:
                self.__extensions[ext_name] = extensions.get(ext_name)

    def on_init(self, case):
        logger.debug(
            'Call to chain callbacks "on_init" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        call_to_chain(
            with_match_layers(self, case), 'on_init', case,
        )

    def on_require(self, case):
        logger.debug(
            'Call to chain callbacks "on_require" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        call_to_chain(
            with_match_layers(self, case), 'on_require', self.__require,
        )

    def on_skip(self, case, reason, result):
        logger.debug(
            'Call to chain callbacks "on_skip" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_skip', case, reason, result,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_skip')
            raise

    def on_any_error(self, error, case, result, tb, timer):
        logger.debug(
            'Call to chain callbacks "on_any_error" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_any_error', error, case, result, tb, timer,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_any_error')
            raise

    def on_error(self, error, case, result, tb, timer):
        logger.debug(
            'Call to chain callbacks "on_error" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_error', error, case, result, tb, timer,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_error')
            raise

    def on_context_error(self, error, case, result, tb, timer):
        logger.debug(
            'Call to chain callbacks "on_context_error" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_context_error', error, case, result, tb, timer,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_context_error')
            raise

    def on_fail(self, fail, case, result, tb, timer):
        logger.debug(
            'Call to chain callbacks "on_fail" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_fail', fail, case, result, tb, timer,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_fail')
            raise

    def on_success(self, case, timer):
        logger.debug(
            'Call to chain callbacks "on_success" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_success', case, timer,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_success')
            raise

    def on_run(self, case):
        logger.debug(
            'Call to chain callbacks "on_run" of case "{}"'.format(
                runnable.class_name(case),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, case), 'on_run', case,
            )
        except BaseException:
            runnable.stopped_on(case, 'on_run')
            raise


assertion = AssertionBase()


class Case(with_metaclass(steps.CaseMeta, runnable.RunnableObject, runnable.MountObjectMixin)):

    __tag__ = None
    __flows__ = None
    __layers__ = None
    __static__ = False
    __require__ = None
    __repeatable__ = True
    __create_reason__ = True
    __always_success__ = False
    __assertion_class__ = None

    #
    # Base components of runnable object
    #

    def __is_run__(self):
        return self.__is_run

    def __is_mount__(self):
        mount_data = getattr(
            self, '__mount_data__', None,
        )
        return isinstance(mount_data, MountData)

    def __method_name__(self):
        return self._method_name

    def __class_name__(self):
        return '{}.{}'.format(
            self.__mount_data__.suite_name, self.__class__.__name__,
        )

    def __reason__(self):
        reasons = []

        if steps.is_step_by_step_case(self):
            history = steps.get_case_history(self) or [None]

            reasons.append(
                reason.join(
                    (
                        reason.item(
                            'History',
                            'was done earlier',
                            *history
                        ),
                        reason.item(
                            'Current step',
                            'when exception was raised',
                            steps.get_current_step(self),
                        ),
                        reason.item(
                            'Current flow',
                            'context of steps execution',
                            steps.get_current_flow(self),
                        ),
                    ),
                ),
            )

        if self.reason_storage:
            reasons.append(
                reason.item(
                    'Case',
                    'info from test case',
                    *(u'{}: {}'.format(k, v) for k, v in self.reason_storage.items())
                ),
            )

        return reason.join(*reasons)

    def __run__(self, result):
        self.__is_run = True
        timer = measure_time()

        if result.current_state.should_stop:
            return

        with result.proxy() as result_proxy:
            result_proxy.start(self)

            if self.__always_success__:
                self.__context.on_success(self)
                result_proxy.add_success(
                    self, timer(),
                )
                return

            if hasattr(self, SKIP_ATTRIBUTE_NAME):
                reason = getattr(self, SKIP_WHY_ATTRIBUTE_NAME, 'no reason')
                self.__context.on_skip(self, reason, result_proxy)
                result_proxy.add_skip(
                    self, reason, timer(),
                )
                return

            self.__log = result_proxy.console.child_console()

            try:
                self.__context.on_run(self)

                was_success = True

                for _ in iter(repeat(self)):
                    with self.__context(self):
                        try:
                            test_method = prepare(
                                self, getattr(self, runnable.method_name(self)),
                            )
                            for _ in iter(repeat_method(self)):
                                test_method()
                        except ALLOW_RAISED_EXCEPTIONS:
                            result_proxy.current_state.should_stop = True
                            raise
                        except Skip as s:
                            runnable.set_debug_if_allowed(self.config)
                            was_success = False
                            self.__context.on_skip(self, s.message, result_proxy)
                            result_proxy.add_skip(
                                self, s.message, timer(),
                            )
                        except AssertionError as fail:
                            runnable.set_debug_if_allowed(self.config)
                            was_success = False
                            tb = traceback.format_exc()
                            self.__context.on_fail(fail, self, result_proxy, tb, timer)
                            result_proxy.add_fail(
                                self, tb, timer(), fail,
                            )
                        except BaseException as error:
                            runnable.set_debug_if_allowed(self.config)
                            was_success = False
                            tb = traceback.format_exc()
                            self.__context.on_error(error, self, result_proxy, tb, timer)
                            self.__context.on_any_error(error, self, result_proxy, tb, timer)
                            result_proxy.add_error(
                                self, tb, timer(), error,
                            )

                    if not was_success:
                        break

                if was_success:
                    self.__context.on_success(self, timer)
                    result_proxy.add_success(
                        self, timer(),
                    )
            except ALLOW_RAISED_EXCEPTIONS:
                raise
            except BaseException as error:
                runnable.set_debug_if_allowed(self.config)
                tb = traceback.format_exc()
                self.__context.on_context_error(error, self, result_proxy, tb, timer)
                self.__context.on_any_error(error, self, result_proxy, tb, timer)
                result_proxy.add_error(
                    self, tb, timer(), error,
                )

    #
    # Behavior on magic methods
    #

    def __str__(self):
        return '{} ({}:{})'.format(
            self._method_name,
            self.__mount_data__.suite_name,
            self.__class__.__name__,
        )

    def __repr__(self):
        class_path = '{}:{}'.format(
            self.__mount_data__.suite_name, self.__class__.__name__,
        )
        return '<{} method_name={} stopped_on={}>'.format(
            class_path, runnable.method_name(self), runnable.stopped_on(self),
        )

    #
    # Self code is starting here
    #

    @runnable.mount_method
    def __init__(self, method_name, config=None, use_flows=True):
        if not hasattr(self, method_name):
            raise AttributeError(
                '"{}" does not have attribute "{}"'.format(
                    self.__class__.__name__,
                    method_name,
                ),
            )

        self.__log = None
        self.__is_run = False
        self.__config = config
        self._method_name = method_name

        if use_flows:
            apply_flows(self)

        self.__context = CaseContext(
            self.setup,
            self.teardown,
            layers=self.__layers__,
        )

        if self.__mount_data__.require:
            self.__context.require.extend(
                self.__mount_data__.require,
            )

        if self.__require__:
            self.__context.require.extend(
                self.__require__,
            )

        if self.__assertion_class__:
            self.__assertion = self.__assertion_class__()
        else:
            self.__assertion = assertion

        self.__context.on_init(self)
        self.__context.on_require(self)

        logger.debug(
            'Install extensions on context of case "{}"'.format(
                runnable.class_name(self),
            ),
        )

        self.__context.install_extensions()

        super(Case, self).__init__()

    @classmethod
    def mount_to(cls, suite, require=None):
        logger.debug(
            'Mount case "{}.{}" to suite "{}"'.format(
                cls.__module__, cls.__name__, suite.name,
            ),
        )

        if getattr(cls, '__mount_data__', None) is not None:
            raise RuntimeError(
                'Case "{}" already mounted'.format(cls.__name__),
            )

        common_require = []

        if require:
            common_require.extend(require)

        if suite.context.require:
            common_require.extend(suite.context.require)

        cls.__mount_data__ = MountData(
            suite_name=suite.name,
            require=common_require,
        )

        return cls

    def __repeat__(self):
        yield

    def __repeat_method__(self):
        yield

    def __prepare__(self, method):
        return method

    @property
    @runnable.mount_method
    def name(self):
        return '{}:{}'.format(
            self.__mount_data__.suite_name,
            self.__class__.__name__
        )

    @property
    def config(self):
        return self.__config

    @property
    @runnable.run_method
    def log(self):
        return self.__log

    @property
    def context(self):
        return self.__context

    @property
    def assertion(self):
        return self.__assertion

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self, *args, **kwargs):
        pass

    def teardown(self, *args, **kwargs):
        pass

    def ext(self, name):
        if name not in self.__context.require:
            raise ExtensionNotRequired(name)

        return self.__context.extensions.get(name)

    @runnable.run_method
    def skip_test(self, reason):
        _skip(reason)(lambda: None)()
