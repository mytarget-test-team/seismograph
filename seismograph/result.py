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


class ResultConsole(object):

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


class ResultMarkers(object):

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

    def support_mp(self, should_stop=None):
        if should_stop:
            self.__should_stop.set(should_stop)

    @property
    def should_stop(self):
        return self.__should_stop.value

    @should_stop.setter
    def should_stop(self, value):
        logger.debug(
            'should_stop on result state did changed. value={}'.format(value),
        )

        self.__should_stop.value = value

    @property
    def runtime(self):
        if self.__result.runtime is not None:
            return self.__result.runtime

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

    __marker_class__ = ResultMarkers

    def __init__(self, config, name=None, stdout=None, current_state=None, is_proxy=False):
        self.errors = []
        self.skipped = []
        self.failures = []
        self.successes = []

        self.proxies = []

        self.__config = config
        self.__is_proxy = is_proxy
        self.__name = name or DEFAULT_NAME
        self.__current_state = current_state or State(self)

        self._stdout = stdout or sys.stdout
        self._marker = self.__marker_class__(self.__config)

        self.__runtime = None
        self.__console = ResultConsole(
            self._stdout,
            verbose=self.__config.VERBOSE,
        )

        if not is_proxy:
            global lock

            if self.__config.GEVENT:
                pyv.check_gevent_supported()

                from gevent.lock import Semaphore

                lock = Semaphore()

            if self.__config.MULTIPROCESSING:
                from multiprocessing import Lock

                lock = Lock()

    def __enter__(self):
        self.print_begin()
        return self

    def __exit__(self, *args, **kwargs):
        self.print_final()

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

    def create_proxy(self, **kwargs):
        logger.debug('Create proxy to result')

        return self.__class__(
            self.__config,
            is_proxy=True,
            stdout=self._stdout,
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
    def proxy(self, runnable_object=None):
        if runnable_object:
            logger.debug(
                'Result proxy will work on runnable object "{}"'.format(
                    runnable.class_name(runnable_object),
                ),
            )

            proxy = self.create_proxy(
                name=runnable.class_name(runnable_object),
            )
            self.proxies.append(proxy)
        else:
            proxy = self.create_proxy()

        try:
            yield proxy
        finally:
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
        self.print_finish(self._marker.error())

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
        self.print_finish(self._marker.fail())

        if self.__config.STOP:
            self.__current_state.should_stop = True

    def add_success(self, runnable_object, runtime):
        xunit_data = xunit.XUnitData(
            runtime=runtime,
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.method_name(runnable_object),
        )

        self.successes.append((runnable_object, xunit_data))
        self.print_finish(self._marker.success())

    def add_skip(self, runnable_object, reason, runtime):
        xunit_data = xunit.XUnitData(
            reason=reason,
            runtime=runtime,
            class_name=runnable.class_name(runnable_object),
            method_name=runnable.method_name(runnable_object),
        )

        self.skipped.append((runnable_object, xunit_data))
        self.print_finish(self._marker.skip(reason))

    def create_report(self, file_path):
        with open(file_path, 'w') as f:
            f.write(
                xunit.create_xml_document(self),
            )

    def print_start(self, runnable_object):
        if self.__config.VERBOSE:
            self.__console.write(
                '* {}: '.format(str(runnable_object)),
            )

    def print_finish(self, status):
        if self.__config.VERBOSE:
            self.__console.writeln(status)
        else:
            self.__console.write(status)

    def print_begin(self):
        self.__console.writeln('Seismograph is measuring:')
        self.__console.line_break()
        self.console.flush()

    def print_final(self):
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

        self.__console.writeln(sep_line)
        self.__console.writeln(total)
        self.__console.flush()
