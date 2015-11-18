# -*- coding: utf-8 -*-

"""
Module for configuration program context
"""

import seismograph.case as _case
import seismograph.xunit as _xunit
import seismograph.suite as _suite
import seismograph.config as _config
import seismograph.reason as _reason
import seismograph.result as _result
import seismograph.loader as _loader
import seismograph.program as _program
import seismograph.runnable as _runnable


shared_data = _program.Program.shared_data
shared_extension = _program.Program.shared_extension


def match_suite_to_layer(cls, layer):
    _suite.MATCH_SUITE_TO_LAYER[cls] = layer


def match_case_to_layer(cls, layer):
    _case.MATCH_CASE_TO_LAYER[cls] = layer


def set_default_case_layers(*layers):
    _case.DEFAULT_LAYERS.extend(layers)


def set_default_suite_layers(*layers):
    _suite.DEFAULT_LAYERS.extend(layers)


def set_default_program_layers(*layers):
    _program.DEFAULT_LAYERS.extend(layers)


def configure(
        reason_class=None,
        config_class=None,
        result_class=None,
        round_runtime=None,
        config_env_name=None,
        test_name_prefix=None,
        case_group_class=None,
        suite_group_class=None,
        default_test_name=None,
        case_context_class=None,
        suite_context_class=None,
        skip_attribute_name=None,
        result_marker_class=None,
        program_context_class=None,
        skip_why_attribute_name=None,
        use_static_test_functions=False):
    if round_runtime:
        assert type(round_runtime) == int
        _xunit.ROUND_RUNTIME = round_runtime

    if use_static_test_functions:
        _case.Case.__static__ = True

    if config_env_name:
        _program.CONFIG_ENV_NAME = config_env_name

    if test_name_prefix:
        _loader.TEST_NAME_PREFIX = test_name_prefix

    if default_test_name:
        _loader.DEFAULT_TEST_NAME = default_test_name

    if skip_attribute_name:
        _case.SKIP_ATTRIBUTE_NAME = skip_attribute_name

    if result_class:
        assert issubclass(result_class, _result.Result)
        _program.Program.__result_class__ = result_class

    if config_class:
        assert issubclass(config_class, _config.Config)
        _program.Program.__config_class__ = config_class

    if skip_why_attribute_name:
        _case.SKIP_WHY_ATTRIBUTE_NAME = skip_why_attribute_name

    if case_group_class:
        assert issubclass(case_group_class, _runnable.RunnableGroup)
        _suite.Suite.__case_group_class__ = case_group_class

    if result_marker_class:
        assert issubclass(result_marker_class, _result.ResultMarkers)
        _result.Result.__marker_class__ = result_marker_class

    if case_context_class:
        assert issubclass(case_context_class, _case.CaseContext)
        _case.CaseContext = case_context_class

    if reason_class:
        assert issubclass(reason_class, _reason.Reason)
        _reason.Reason = reason_class

    if suite_context_class:
        assert issubclass(suite_context_class, _suite.SuiteContext)
        _suite.SuiteContext = suite_context_class

    if program_context_class:
        assert issubclass(program_context_class, _program.ProgramContext)
        _program.ProgramContext = program_context_class

    if suite_group_class:
        assert issubclass(suite_group_class, _runnable.RunnableGroup)
        _program.Program.__suite_group_class__ = suite_group_class
