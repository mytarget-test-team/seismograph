# -*- coding: utf-8 -*-

import logging
import traceback
from types import FunctionType

from . import case
from . import reason
from . import loader
from . import runnable
from . import extensions
from .utils.common import measure_time
from .utils.common import call_to_chain
from .groups.default import DefaultCaseGroup
from .exceptions import ExtensionNotRequired
from .exceptions import ALLOW_RAISED_EXCEPTIONS


logger = logging.getLogger(__name__)


DEFAULT_LAYERS = []
MATCH_SUITE_TO_LAYER = {}


def with_match_layers(context, suite):
    for layer in context.layers:
        yield layer

    for cls, layer in MATCH_SUITE_TO_LAYER.items():
        if isinstance(suite, cls) and layer.enabled:
            yield layer


class MountData(object):

    def __init__(self, config=None):
        self.__config = config

    @property
    def config(self):
        return self.__config


class BuildRule(object):

    def __init__(self, suite_name, case_name=None, test_name=None):
        self.__suite_name = suite_name
        self.__case_name = case_name
        self.__test_name = test_name

    def __str__(self):
        if self.__suite_name and self.__case_name and self.__test_name:
            return '{}:{}.{}'.format(
                self.__suite_name, self.__case_name, self.__test_name,
            )

        if self.__suite_name and self.__case_name:
            return '{}:{}'.format(
                self.__suite_name, self.__case_name,
            )

        return self.__suite_name

    def __repr__(self):
        return '<{}(suite_name={}, case_name={}, test_name={})>'.format(
            self.__class__.__name__,
            self.__suite_name,
            self.__case_name,
            self.__test_name,
        )

    @property
    def suite_name(self):
        return self.__suite_name

    @property
    def case_name(self):
        return self.__case_name

    @property
    def test_name(self):
        return self.__test_name

    def is_of(self, suite):
        return self.__suite_name == suite.name


class SuiteContext(runnable.ContextOfRunnableObject):

    def __init__(self, setup, teardown):
        self.__layers = []
        self.__require = []

        self.__extensions = {}
        self.__build_rules = []

        self.__setup_callbacks = [setup]
        self.__teardown_callbacks = [teardown]

    @property
    def require(self):
        return self.__require

    @property
    def extensions(self):
        return self.__extensions

    @property
    def build_rules(self):
        return self.__build_rules

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

    def add_layers(self, layers):
        self.__layers.extend(layers)

    def install_extensions(self):
        for ext_name in self.__require:
            if ext_name not in self.__extensions:
                self.__extensions[ext_name] = extensions.get(ext_name)

    def start_context(self, suite):
        logger.debug(
            'Start context of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, suite), 'on_setup', suite,
            )
            call_to_chain(self.__setup_callbacks, None)
        except BaseException:
            runnable.stopped_on(suite, 'start_context')
            raise

    def stop_context(self, suite):
        logger.debug(
            'Stop context of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, suite), 'on_teardown', suite,
            )
            call_to_chain(self.__teardown_callbacks, None)
        except BaseException:
            runnable.stopped_on(suite, 'stop_context')
            raise

    def on_init(self, suite):
        logger.debug(
            'Call to chain callbacks "on_init" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        call_to_chain(
            with_match_layers(self, suite), 'on_init', suite,
        )

    def on_require(self, suite):
        logger.debug(
            'Call to chain callbacks "on_require" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        call_to_chain(
            with_match_layers(self, suite), 'on_require', self.__require,
        )

    def on_build_rule(self, suite, rule):
        logger.debug(
            'Call to chain callbacks "on_build_rule" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        call_to_chain(
            with_match_layers(self, suite), 'on_build_rule', suite, rule,
        )

    def on_mount(self, suite, program):
        logger.debug(
            'Call to chain callbacks "on_mount" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        call_to_chain(
            with_match_layers(self, suite), 'on_mount', suite, program,
        )

    def on_run(self, suite):
        logger.debug(
            'Call to chain callbacks "on_run" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, suite), 'on_run', suite,
            )
        except BaseException:
            runnable.stopped_on(suite, 'on_run')
            raise

    def on_error(self, error, suite, result, tb, timer):
        logger.debug(
            'Call to chain callbacks "on_error" of suite "{}"'.format(
                runnable.class_name(suite),
            ),
        )

        try:
            call_to_chain(
                with_match_layers(self, suite), 'on_error', error, suite, result, tb, timer,
            )
        except BaseException:
            runnable.stopped_on(suite, 'on_error')
            raise


class Suite(runnable.RunnableObject, runnable.MountObjectMixin, runnable.BuildObjectMixin):

    __layers__ = None
    __require__ = None
    __create_reason__ = True
    __case_class__ = case.Case
    __case_group_class__ = None
    __case_box_class__ = case.CaseBox

    #
    # Base components of runnable object
    #

    def __is_run__(self):
        return self.__is_run

    def __is_build__(self):
        return self.__is_build

    def __is_mount__(self):
        return isinstance(self.__mount_data__, MountData)

    def __class_name__(self):
        return self.__name

    def __reason__(self):
        if self.reason_storage:
            return reason.item(
                'Suite',
                'info from suite',
                *(u'{}: {}'.format(k, v) for k, v in self.reason_storage.items())
            )
        return ''

    @runnable.build_method
    def __run__(self, result):
        self.__is_run = True
        timer = measure_time()

        if result.current_state.should_stop or not self.__case_instances:
            return

        group = self._make_group()

        with result.proxy(self, timer=timer) as result_proxy:
            try:
                self.__context.on_run(self)

                with self.__context(self):
                    group(result_proxy)
            except ALLOW_RAISED_EXCEPTIONS:
                raise
            except BaseException as error:
                runnable.set_debug_if_allowed(self.config)
                tb = traceback.format_exc()
                self.__context.on_error(error, self, result_proxy, tb, timer)
                result_proxy.add_error(
                    self, tb, timer(), error,
                )

    #
    # Behavior on magic methods
    #

    def __iter__(self):
        return iter(self.__case_instances)

    def __nonzero__(self):
        return bool(self.__case_instances)

    def __bool__(self):  # please python 3
        return self.__nonzero__()

    #
    # Self code is starting here
    #

    def __init__(self, name, require=None, layers=None):
        super(Suite, self).__init__()

        self.__name = name

        self.__is_run = False
        self.__is_build = False

        self.__case_classes = []
        self.__case_instances = []

        self.__mount_data__ = None

        self.__context = SuiteContext(self.setup, self.teardown)

        if self.__layers__:
            self.__context.add_layers(self.__layers__)

        if layers:
            self.__context.add_layers(layers)

        if require:
            self.__context.require.extend(require)

        if self.__require__:
            self.__context.require.extend(self.__require__)

        self.__context.on_init(self)
        self.__context.on_require(self)

    def __build__(self, case_name=None, test_name=None):
        logger.debug(
            'Build suite "{}". case=name={} test_name={}'.format(
                runnable.class_name(self), case_name, test_name,
            ),
        )

        if test_name and not case_name:
            raise AssertionError(
                'test name can not be installed without case name',
            )

        if case_name:
            cls = loader.load_case_from_suite(
                case_name, self,
            )

            if self.config.SPLIT_FLOWS:
                case_classes = loader.load_separated_classes_for_flows(cls)
            else:
                case_classes = [cls]

        else:
            if self.config.SPLIT_FLOWS:
                case_classes = []

                for case_class in self.__case_classes:
                    case_classes.extend(
                        loader.load_separated_classes_for_flows(case_class),
                    )
            else:
                case_classes = self.__case_classes

        for cls in case_classes:
            self.__case_instances.extend(
                loader.load_tests_from_case(
                    cls,
                    config=self.config,
                    method_name=test_name,
                    box_class=self.__case_box_class__,
                ),
            )

    @property
    def name(self):
        return self.__name

    @property
    @runnable.mount_method
    def config(self):
        return self.__mount_data__.config

    @property
    def cases(self):
        return self.__case_classes

    @property
    def context(self):
        return self.__context

    def _make_group(self):
        if self.__case_group_class__:
            logger.debug(
                'Use "__case_group_class__" to making case group',
            )

            return self.__case_group_class__(
                self.__case_instances, self.config,
            )

        if self.config.GEVENT:
            logger.debug(
                'Use "GeventCaseGroup" to making case group',
            )

            from .groups.gevent import GeventCaseGroup

            return GeventCaseGroup(
                self.__case_instances, self.config,
            )

        if self.config.THREADING or self.config.MULTIPROCESSING:
            logger.debug(
                'Use "ThreadingCaseGroup" to making case group',
            )

            from .groups.threading import ThreadingCaseGroup

            return ThreadingCaseGroup(
                self.__case_instances, self.config,
            )

        logger.debug(
            'Use "DefaultCaseGroup" to making case group',
        )

        return DefaultCaseGroup(
            self.__case_instances, self.config,
        )

    def setup(self, *args, **kwargs):
        pass

    def teardown(self, *args, **kwargs):
        pass

    def add_setup(self, f):
        self.__context.setup_callbacks.append(f)
        return f

    def add_teardown(self, f):
        self.__context.teardown_callbacks.append(f)
        return f

    def assign_build_rule(self, rule):
        """
        :type rule: BuildRule
        """
        self.__context.on_build_rule(self, rule)

        assert rule.is_of(self), 'Build rule "{}" is not of this suite'.format(
            str(rule),
        )

        if rule.case_name:
            self.__context.build_rules.append(rule)

    @runnable.build_method
    def ext(self, name):
        if name not in self.__context.require:
            raise ExtensionNotRequired(name)

        return self.__context.extensions.get(name)

    def mount_to(self, program):
        logger.debug(
            'Mount suite to program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        if runnable.is_mount(self):
            raise RuntimeError(
                'Suite "{}" already mount'.format(self.__name),
            )

        program.suites.append(self)

        self.__mount_data__ = MountData(
            config=program.config,
        )

        self.__context.on_mount(self, program)

    def get_map(self):
        mp = {}

        for case_class in self.__case_classes:
            mp[case_class.__name__] = {
                'cls': case_class,
                'tests': dict(
                    (atr, getattr(case_class, atr))
                    for atr in dir(case_class)
                    if atr.startswith(loader.TEST_NAME_PREFIX)
                    or
                    atr == loader.DEFAULT_TEST_NAME,
                ),
            }

        return mp

    def register(self, cls=None, **kwargs):
        if not cls and not kwargs:
            raise TypeError('cls param or **kwargs is required')
        elif cls and kwargs:
            raise TypeError('**kwargs can not be used with cls param')

        def wrapped(
                _class,
                skip=None,
                flows=None,
                layers=None,
                static=False,
                require=None,
                case_class=None,
                always_success=False,
                assertion_class=None,
                tag=None):
            logger.debug(
                'Register case "{}.{}" on suite "{}"'.format(
                    _class.__module__, _class.__name__, self.name,
                ),
            )

            if type(_class) == FunctionType:
                _class = case.make_case_class_from_function(
                    _class,
                    static=static,
                    base_class=case_class or self.__case_class__,
                )

            if tag:
                setattr(_class, '__tag__', tag)

            if skip:
                case.skip(skip)(_class)

            if flows:
                setattr(_class, '__flows__', flows)

            if always_success:
                setattr(_class, '__always_success__', True)

            if layers:
                if _class.__layers__:
                    _class.__layers__ = tuple(_class.__layers__) + tuple(layers)
                else:
                    _class.__layers__ = tuple(layers)

            if assertion_class:
                setattr(_class, '__assertion_class__', assertion_class)

            self.__case_classes.append(
                _class.mount_to(
                    self,
                    require=require,
                ),
            )

            return _class

        if cls:
            return wrapped(cls)

        def wrapper(_class):
            return wrapped(_class, **kwargs)

        return wrapper

    @runnable.mount_method
    def build(self, case_name=None, test_name=None, shuffle=None):
        if self.__is_build:
            raise RuntimeError(
                'Suite "{}" is already built'.format(
                    self.__class__.__name__,
                ),
            )

        logger.debug(
            'Install extensions on context of suite "{}"'.format(self.name),
        )

        self.__context.install_extensions()

        if self.__context.build_rules and not case_name:
            for rule in self.__context.build_rules:
                self.__build__(
                    case_name=rule.case_name,
                    test_name=rule.test_name,
                )
        else:
            self.__build__(
                case_name=case_name,
                test_name=test_name,
            )

        if shuffle:
            shuffle(self.__case_instances)

        self.__is_build = True
