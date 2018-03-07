# -*- coding: utf-8 -*-

import sys
import inspect
from functools import wraps

from . import loader
from . import runnable
from .utils import pyv


STEP_ATTRIBUTE_NAME = '__step__'
STEP_DOC_ATTRIBUTE_NAME = '__doc__'
STEP_WEIGHT_ATTRIBUTE_NAME = '__weight__'
STEPS_HISTORY_ATTRIBUTE_NAME = '__history__'
CURRENT_STEP_ATTRIBUTE_NAME = '__current_step__'
CURRENT_FLOW_ATTRIBUTE_NAME = '__current_flow__'
STEP_BY_STEP_ATTRIBUTE_NAME = '__step_by_step__'
STEPS_STORAGE_ATTRIBUTE_NAME = '__step_methods__'


def step(num, doc=None, performer=None, for_flows=None):
    def wrapper(method):
        if type(num) not in (int, float):
            raise ValueError('step num can be int or float type only')

        setattr(method, STEP_DOC_ATTRIBUTE_NAME, doc or '')
        setattr(method, STEP_WEIGHT_ATTRIBUTE_NAME, num)
        setattr(method, STEP_ATTRIBUTE_NAME, True)

        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if for_flows:
                flows = getattr(self, '__flows__', [])
                current_flow = get_current_flow(self)
                is_able_to_run = (
                    flows.index(current_flow) + 1 in for_flows
                )
                if not is_able_to_run:
                    return

            if performer:
                return performer(self, lambda: _call_to_method(self, method, *args, **kwargs))
            return _call_to_method(self, method, *args, **kwargs)

        return wrapped

    return wrapper


def get_step_methods(case):
    return getattr(case, STEPS_STORAGE_ATTRIBUTE_NAME)


def get_case_name(case):
    return case.__class__.__name__


def get_step_doc(method):
    return pyv.unicode_string(
        getattr(method, STEP_DOC_ATTRIBUTE_NAME),
    )


def is_step_by_step_case(case):
    return hasattr(case, STEP_BY_STEP_ATTRIBUTE_NAME)


def get_current_step(case):
    return pyv.unicode_string(
        getattr(case, CURRENT_STEP_ATTRIBUTE_NAME),
    )


def get_current_flow(case):
    return getattr(case, CURRENT_FLOW_ATTRIBUTE_NAME)


def get_step_num(method):
    return getattr(method, STEP_WEIGHT_ATTRIBUTE_NAME)


def get_case_history(case):
    return getattr(case, STEPS_HISTORY_ATTRIBUTE_NAME)


def _create_history_line(method):
    return u'{}. {}'.format(
        get_step_num(method),
        get_step_doc(method),
    )


def _create_current_step_info(case, method):
    return u'<{}.{}({}): {}>'.format(
        get_case_name(case),
        pyv.get_func_name(method),
        get_step_num(method),
        get_step_doc(method),
    )


def _step_log(case, method, flow):
    doc = get_step_doc(method)
    num = get_step_num(method)
    case_name = get_case_name(case)
    method_name = pyv.get_func_name(method)

    return u'{}{}. {}.{}: "{}"'.format(
        ''.join(' ' for _ in pyv.xrange(4 if flow else 2)),
        num, case_name, method_name, doc,
    )


def _perform_prompt(case, method, exit_code=None):
    commands = {  # prompt commands
        'exit': 'q',
        'continue': 'c',
    }
    prompt = '>> {}.{} [{}]: '.format(
        case.__class__.__name__,
        pyv.get_func_name(method),
        ', '.join([c for _, c in commands.items()]),
    )
    command = case.log.prompt(prompt).strip()

    if command == commands['exit']:
        sys.exit(exit_code or 0)


def _run_step(case, method, flow=None):
    if case.config.STEP_BY_STEP:
        _perform_prompt(case, method)

    if case.config.STEPS_LOG:
        case.log(_step_log(case, method, flow))

    try:
        if flow is not None:
            method(case, flow)
        else:
            method(case)
    except BaseException:
        runnable.stopped_on(case, pyv.get_func_name(method))
        raise


def _call_to_method(case, method, *args, **kwargs):
    sig = inspect.getargspec(method)

    if len(sig.args) == 1 and not sig.varargs and not sig.keywords:
        return method(case) if case else method()

    return method(case, *args, **kwargs) if case else method(*args, **kwargs)


def _call_to_begin_method_if_exist(case, flow=None):
    if getattr(case, 'begin', False):
        setattr(
            case,
            CURRENT_STEP_ATTRIBUTE_NAME,
            'begin',
        )
        if flow is not None:
            return _call_to_method(None, case.begin, flow)
        return case.begin()


def _call_to_finish_method_if_exist(case, flow=None):
    if getattr(case, 'finish', False):
        setattr(
            case,
            CURRENT_STEP_ATTRIBUTE_NAME,
            'finish',
        )
        if flow is not None:
            return _call_to_method(None, case.finish, flow)
        return case.finish()


def _make_run_test():
    def run_test(self):
        run_test.__doc__ = self.__doc__

        if self.__flows__:

            for flow in self.__flows__:
                _call_to_begin_method_if_exist(self, flow=flow)

                setattr(self, CURRENT_FLOW_ATTRIBUTE_NAME, flow)

                if self.config.STEPS_LOG:
                    self.log(u'  Flow: ', pyv.unicode_string(flow))

                try:
                    for step_method in get_step_methods(self):
                        setattr(
                            self,
                            CURRENT_STEP_ATTRIBUTE_NAME,
                            _create_current_step_info(self, step_method),
                        )
                        getattr(self, STEPS_HISTORY_ATTRIBUTE_NAME).append(
                            _create_history_line(step_method),
                        )

                        _run_step(self, step_method, flow=flow)
                    else:
                        setattr(self, STEPS_HISTORY_ATTRIBUTE_NAME, [])
                finally:
                    _call_to_finish_method_if_exist(self, flow=flow)

                if self.config.FIRST_FLOW_ONLY:
                    break

        else:
            _call_to_begin_method_if_exist(self)

            for step_method in get_step_methods(self):
                setattr(
                    self,
                    CURRENT_STEP_ATTRIBUTE_NAME,
                    _create_current_step_info(self, step_method),
                )
                getattr(self, STEPS_HISTORY_ATTRIBUTE_NAME).append(
                    _create_history_line(step_method),
                )

                _run_step(self, step_method)

            _call_to_finish_method_if_exist(self)

    return run_test


class CaseMeta(type):

    def __new__(mcs, name, bases, dct):
        cls = type.__new__(mcs, name, bases, dct)

        steps = []

        attributes = (
            a for a in dir(cls)
            if not a.startswith('_')
        )

        for atr in attributes:
            method = getattr(cls, atr, None)
            if hasattr(method, STEP_ATTRIBUTE_NAME):
                steps.append(method)

        if steps:
            steps.sort(
                key=lambda m: getattr(m, STEP_WEIGHT_ATTRIBUTE_NAME),
            )

            setattr(cls, STEPS_HISTORY_ATTRIBUTE_NAME, [])
            setattr(cls, CURRENT_STEP_ATTRIBUTE_NAME, None)
            setattr(cls, STEP_BY_STEP_ATTRIBUTE_NAME, True)
            setattr(cls, STEPS_STORAGE_ATTRIBUTE_NAME, steps)
            setattr(cls, CURRENT_FLOW_ATTRIBUTE_NAME, 'Without flows')
            setattr(cls, loader.DEFAULT_TEST_NAME, _make_run_test())

        return cls
