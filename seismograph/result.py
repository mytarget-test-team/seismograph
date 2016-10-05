# -*- coding: utf-8 -*-

import sys
import logging
from threading import Lock
from contextlib import contextmanager

from . import xunit
from . import reason
from . import runnable
from .utils import pyv
from .utils import colors
from .utils.mp import MPSupportedValue


lock = Lock()
logger = logging.getLogger(__name__)


DEFAULT_NAME = 'seismograph'
START_MESSAGE = 'Seismograph is measuring'


def get_runnable_from_storage_item(item):
    runnable_object, _ = item
    return runnable_object


def get_xunit_data_from_storage_item(item):
    _, xunit_data = item
    return xunit_data


def get_last_item_from_storage(storage):
    if storage:
        return storage[len(storage) - 1]
    return None


def get_xunit_data_from_storage(storage, runnable_object):
    for item in storage:
        if get_runnable_from_storage_item(item) == runnable_object:
            return get_xunit_data_from_storage_item(item)
    return None


def reset_item_of_storage(storage, runnable_object, xunit_data):
    assert isinstance(xunit_data, xunit.XUnitData)

    for item in storage:
        if get_runnable_from_storage_item(item) == runnable_object:
            storage.remove(item)
            storage.append((runnable_object, xunit_data))
            return True

    return False


def get_runtime_from_storage(storage):
    rt = float()
    for item in storage:
        rt += get_xunit_data_from_storage_item(item).runtime
    return rt


class CaptureStream(object):

    def __init__(self):
        self.__buffer = []

    def __getattr__(self, item):
        return getattr(sys.stderr, item)

    def write(self, s):
        self.__buffer.append(s)

    def flush(self, fp=None):
        if fp and self.__buffer:
            with lock:
                fp.write('\nLogging capture:\n\n')
                for s in self.__buffer:
                    fp.write(s)
                    fp.flush()
            self.__buffer = []


class LogCapture(object):

    was_captured = []
    stream = CaptureStream()

    def __init__(self, config):
        self.__config = config

    def __bool__(self):
        return self.__nonzero__()

    def __nonzero__(self):
        return not self.__config.NO_CAPTURE

    @property
    def loggers(self):
        for _, logger in logging.Logger.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                yield logger

    def make(self):
        for logger in self.loggers:
            if logger in self.was_captured:
                continue

            for handler in logger.handlers:
                if handler.__class__ == logging.StreamHandler:
                    handler.stream = self.stream

            self.was_captured.append(logger)

    def flush(self, fp):
        self.stream.flush(fp)


class Console(object):

    class ChildConsole(object):

        TAB = 2  # tab to spaces
        DEFAULT_TABS = 1

        def __init__(self):
            self.__buffer = []
            self.__tabs = self.DEFAULT_TABS * self.TAB

        def __call__(self, *strings):
            string = []

            for s in strings:
                if not isinstance(s, pyv.basestring):
                    s = pyv.unicode_string(s)
                string.append(s)

            self.__buffer.append(
                ''.join(' ' for _ in pyv.xrange(self.__tabs)) + u''.join(string) + '\n',
            )

        @property
        def set_trace(self):
            try:
                import ipdb as pdb
            except ImportError:
                import pdb
            return pdb.set_trace

        @staticmethod
        def prompt(prompt=None):
            return raw_input(prompt)

        @contextmanager
        def ul(self, title=None, numerate=False):
            li = []

            yield lambda s: li.append(s)

            if title:
                self(u'{}:'.format(title))
            for l in li:
                self(
                    u'{}{} {}'.format(
                        ''.join(' ' for _ in pyv.xrange(self.__tabs)),
                        '{}.'.format(li.index(l) + 1) if numerate else '*', l,
                    ),
                )

        @contextmanager
        def tab(self):
            current_tabs = self.__tabs
            self.__tabs = current_tabs + self.TAB
            yield
            self.__tabs = current_tabs

        def flush(self, stream):
            stream.write(
                u''.join(self.__buffer),
            )
            self.__buffer = []

    def __init__(self, stream=None, verbose=False):
        self.__buffer = []
        self.__children = []

        self.__verbose = verbose
        self.__stream = stream or sys.stdout

    def __call__(self, string):
        self.writeln(string)
        self.flush()

    def child_console(self):
        child_console = self.ChildConsole()
        self.__children.append(child_console)
        return child_console

    def flush(self):
        with lock:
            self.__stream.write(
                u''.join(self.__buffer),
            )
            for child in self.__children:
                child.flush(self.__stream)

            self.__stream.flush()

        self.__buffer = []

    def write(self, string):
        self.__buffer.append(string)

    def writeln(self, string):
        self.write(string + '\n')

    def line_break(self):
        self.writeln('')


class Markers(object):

        LONG_FAIL = 'FAIL'
        LONG_SKIP = 'SKIP: '
        LONG_SUCCESS = 'OK'
        LONG_ERROR = 'ERROR'

        SMALL_FAIL = 'F'
        SMALL_SKIP = 'S'
        SMALL_ERROR = 'E'
        SMALL_SUCCESS = '.'

        def __init__(self, config):
            self.__config = config

        @property
        def config(self):
            return self.__config

        def fail(self):
            if self.__config.VERBOSE:
                if self.__config.NO_COLOR:
                    return self.LONG_FAIL
                return colors.yellow(self.LONG_FAIL)
            if self.__config.NO_COLOR:
                return self.SMALL_FAIL
            return colors.yellow(self.SMALL_FAIL)

        def skip(self, reason):
            if self.__config.VERBOSE:
                if self.__config.NO_COLOR:
                    return u'{}{}'.format(self.LONG_SKIP, reason)
                return u'{}{}'.format(colors.blue(self.LONG_SKIP), reason)
            if self.__config.NO_COLOR:
                return self.SMALL_SKIP
            return colors.blue(self.SMALL_SKIP)

        def success(self):
            if self.__config.VERBOSE:
                if self.__config.NO_COLOR:
                    return self.LONG_SUCCESS
                return colors.green(self.LONG_SUCCESS)
            return self.SMALL_SUCCESS

        def error(self):
            if self.__config.VERBOSE:
                if self.__config.NO_COLOR:
                    return self.LONG_ERROR
                return colors.red(self.LONG_ERROR)
            if self.__config.NO_COLOR:
                return self.SMALL_ERROR
            return colors.red(self.SMALL_ERROR)


class State(object):

    def __init__(self, result, should_stop=False):
        self.__result = result
        self.__should_stop = MPSupportedValue(should_stop)

    def support_mp(self, manager):
        self.__should_stop.set(
            manager.Value('b', self.should_stop)
        )

    @property
    def should_stop(self):
        return self.__should_stop.value

    @should_stop.setter
    def should_stop(self, value):
        self.__should_stop.value = value

        logger.debug(
            '"should_stop" on result state did changed. value={}'.format(value),
        )

    @property
    def runtime(self):
        if self.__result.runtime is not None:
            return round(self.__result.runtime, xunit.ROUND_RUNTIME)

        runtime = float()

        for storage in (
                self.__result.errors,
                self.__result.skipped,
                self.__result.failures,
                self.__result.successes):
            runtime += get_runtime_from_storage(storage)

        return round(runtime, xunit.ROUND_RUNTIME)

    @property
    def tests(self):
        return self.errors + self.successes + self.failures + self.skipped

    @property
    def errors(self):
        return len(self.__result.errors)

    @property
    def successes(self):
        return len(self.__result.successes)

    @property
    def failures(self):
        return len(self.__result.failures)

    @property
    def skipped(self):
        return len(self.__result.skipped)

    @property
    def was_success(self):
        return not self.__result.errors and not self.__result.failures


class Result(object):

    __marker_class__ = Markers

    def __init__(self, config, name=None, stream=None, current_state=None, is_proxy=False):
        self.errors = []
        self.skipped = []
        self.failures = []
        self.successes = []

        self.proxies = []

        self.__config = config
        self.__is_proxy = is_proxy
        self.__name = name or DEFAULT_NAME
        self.__current_state = current_state or State(self)

        self._stream = stream or sys.stdout
        self._marker = self.__marker_class__(self.__config)

        self.__timer = None
        self.__runtime = None
        self.__capture = None
        self.__console = Console(
            self._stream,
            verbose=self.__config.VERBOSE,
        )

        if not is_proxy:
            global lock

            self.__capture = LogCapture(config)

            if self.__config.GEVENT:
                from gevent.lock import Semaphore

                lock = Semaphore()

            if self.__config.MULTIPROCESSING:
                from multiprocessing import Lock

                lock = Lock()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, *args, **kwargs):
        self.final()

        if self.__config.XUNIT_REPORT:
            self.create_report(self.__config.XUNIT_REPORT)

    def __repr__(self):
        state = self.get_state()
        return '<Result(tests={}, failures={}, errors={}, skipped={} success={})>'.format(
            state.tests,
            state.failures,
            state.errors,
            state.skipped,
            state.successes,
        )

    @property
    def name(self):
        return self.__name

    @property
    def is_proxy(self):
        return self.__is_proxy

    @property
    def config(self):
        return self.__config

    @property
    def capture(self):
        return self.__capture

    @property
    def console(self):
        return self.__console

    @property
    def runtime(self):
        return self.__runtime

    @runtime.setter
    def runtime(self, value):
        self.__runtime = value

    @property
    def current_state(self):
        return self.__current_state

    def support_mp(self, manager):
        self.__current_state.support_mp(manager)

    def set_timer(self, timer):
        self.__timer = timer

    def stop_timer(self):
        if self.__timer:
            self.__runtime = self.__timer()

    def create_proxy(self, **kwargs):
        logger.debug('Create proxy to result')

        return self.__class__(
            self.__config,
            is_proxy=True,
            stream=self._stream,
            current_state=self.__current_state,
            **kwargs
        )

    def extend(self, result):
        assert result.is_proxy, 'result can not be extended from no proxy'

        logger.debug(
            'Extend result "{}" from proxy "{}"'.format(
                self.name, result.name
            ),
        )

        self.errors.extend(result.errors)
        self.skipped.extend(result.skipped)
        self.failures.extend(result.failures)
        self.successes.extend(result.successes)

    @contextmanager
    def proxy(self, runnable_object=None, timer=None):
        if runnable_object:
            logger.debug(
                'Result proxy will work on runnable object "{}"'.format(
                    runnable.class_name(runnable_object),
                ),
            )

            proxy = self.create_proxy(
                name=runnable.class_name(runnable_object),
            )
            proxy.set_timer(timer)

            self.proxies.append(proxy)
        else:
            proxy = self.create_proxy()

        try:
            yield proxy
        finally:
            proxy.stop_timer()
            self.extend(proxy)
            proxy.console.flush()

    def get_state(self):
        return State(
            self, should_stop=self.__current_state.should_stop,
        )

    def get_fail_by(self, runnable_object):
        return get_xunit_data_from_storage(self.failures, runnable_object)

    def reset_fail(self, runnable_object, xunit_data):
        return reset_item_of_storage(self.failures, runnable_object, xunit_data)

    def get_error_by(self, runnable_object):
        return get_xunit_data_from_storage(self.errors, runnable_object)

    def reset_error(self, runnable_object, xunit_data):
        return reset_item_of_storage(self.errors, runnable_object, xunit_data)

    def get_skip_by(self, runnable_object):
        return get_xunit_data_from_storage(self.skipped, runnable_object)

    def reset_skip(self, runnable_object, xunit_data):
        return reset_item_of_storage(self.skipped, runnable_object, xunit_data)

    def get_success_by(self, runnable_object):
        return get_xunit_data_from_storage(self.successes, runnable_object)

    def reset_success(self, runnable_object, xunit_data):
        return reset_item_of_storage(self.successes, runnable_object, xunit_data)

    def add_error(self, runnable_object, traceback, runtime, exc):
        error_reason = reason.create(
            runnable_object, traceback, config=self.__config,
        )

        xunit_data = xunit.XUnitData(
            exc=exc,
            runtime=runtime,
            reason=reason.format_reason(error_reason),
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.stopped_on(runnable_object),
        )

        self.errors.append((runnable_object, xunit_data))
        self.finish(self._marker.error())

        if self.__config.STOP:
            self.__current_state.should_stop = True

    def add_fail(self, runnable_object, traceback, runtime, exc):
        fail_reason = reason.create(
            runnable_object, traceback, config=self.__config,
        )

        xunit_data = xunit.XUnitData(
            exc=exc,
            runtime=runtime,
            reason=reason.format_reason(fail_reason),
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.stopped_on(runnable_object),
        )

        self.failures.append((runnable_object, xunit_data))
        self.finish(self._marker.fail())

        if self.__config.STOP:
            self.__current_state.should_stop = True

    def add_success(self, runnable_object, runtime):
        xunit_data = xunit.XUnitData(
            runtime=runtime,
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.method_name(runnable_object),
        )

        self.successes.append((runnable_object, xunit_data))
        self.finish(self._marker.success())

    def add_skip(self, runnable_object, reason, runtime):
        xunit_data = xunit.XUnitData(
            reason=reason,
            runtime=runtime,
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.method_name(runnable_object),
        )

        self.skipped.append((runnable_object, xunit_data))
        self.finish(self._marker.skip(reason))

    def create_report(self, file_path):
        if self.__is_proxy:
            raise RuntimeError(
                'Proxy result can not be independent',
            )

        with open(file_path, 'w') as f:
            f.write(
                xunit.create_xml_document(self),
            )

    def start(self, runnable_object):
        if self.__config.VERBOSE:
            self.__console.write(
                '* {}: '.format(str(runnable_object)),
            )

    def finish(self, status):
        if self.__config.VERBOSE:
            self.__console.writeln(status)
        else:
            self.__console.write(status)

    def begin(self):
        if self.__is_proxy:
            raise RuntimeError(
                'Proxy result can not be independent',
            )

        if self.__capture:
            self.__capture.make()

        self.__console.writeln(u'{}:'.format(START_MESSAGE))
        self.__console.line_break()
        self.console.flush()

    def final(self):
        if self.__is_proxy:
            raise RuntimeError(
                'Proxy result can not be independent',
            )

        if not self.__config.VERBOSE:
            self.__console.line_break()

        need_report = bool(self.errors or self.failures)

        if need_report:
            self.__console.line_break()
            self.__console.writeln(
                'Seismograph is reporting about reasons:',
            )
            self.__console.line_break()

            for storage in (self.errors, self.failures):
                for storage_item in storage:
                    runnable_object, xunit_data = storage_item
                    if xunit_data.reason:
                        crash_reason = reason.create(
                            runnable_object, xunit_data.reason, config=self.__config,
                        )
                        self.__console.writeln(
                            reason.format_reason_to_output(crash_reason),
                        )

        total = 'tests={} failures={} errors={} skipped={} successes={} runtime={}'.format(
            self.__current_state.tests,
            self.__current_state.failures,
            self.__current_state.errors,
            self.__current_state.skipped,
            self.__current_state.successes,
            self.__current_state.runtime,
        )

        sep_line = ''.join(
            '-' for _ in pyv.xrange(len(total)),
        )

        if not need_report:
            self.__console.line_break()

        if self.config.SUITE_DETAIL:
            self.__console.writeln(sep_line)

            for proxy in self.proxies:
                state = proxy.get_state()

                self.__console.writeln(
                    '{}: {}'.format(
                        proxy.name, state.runtime,
                    ),
                )

        self.__console.writeln(sep_line)
        self.__console.writeln(total)
        self.__console.flush()

        if self.__capture:
            self.__capture.flush(self._stream)
