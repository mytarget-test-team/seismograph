# -*- coding: utf-8 -*-

import os
import imp
import time
import logging
from optparse import OptionGroup
from optparse import OptionParser
from importlib import import_module

from .utils import pyv
from .exceptions import ConfigError
from .datastructures import DictObject


logger = logging.getLogger(__name__)


def create_option_parser():
    parser = OptionParser('seismograph <suites_path> [options]')

    result_group = OptionGroup(parser, 'Result options')
    result_group.add_option(
        '--xunit-report',
        dest='XUNIT_REPORT',
        default=None,
        help='Path to xml file to store the xunit report in.',
    )
    parser.add_option_group(result_group)

    console_group = OptionGroup(parser, 'Output options')
    console_group.add_option(
        '-v', '--verbose',
        action='store_true',
        dest='VERBOSE',
        default=False,
        help='Detail output.',
    )
    console_group.add_option(
        '-o', '--output',
        type=str,
        dest='OUTPUT',
        default=None,
        help='Redirect output to file.',
    )
    console_group.add_option(
        '--no-capture',
        dest='NO_CAPTURE',
        action='store_true',
        default=False,
        help='No capture log.',
    )
    console_group.add_option(
        '--suite-detail',
        action='store_true',
        dest='SUITE_DETAIL',
        default=False,
        help='Detail stat from suites.',
    )
    console_group.add_option(
        '--tree',
        dest='TREE',
        action='store_true',
        default=False,
        help='Print tree of suites to console.',
    )
    console_group.add_option(
        '--no-color',
        dest='NO_COLOR',
        action='store_true',
        default=False,
        help='No use color on output.',
    )
    parser.add_option_group(console_group)

    case_group = OptionGroup(parser, 'Case options')
    case_group.add_option(
        '--steps-log',
        dest='STEPS_LOG',
        action='store_true',
        default=False,
        help='Print history of steps to console.',
    )
    case_group.add_option(
        '--flows-log',
        dest='FLOWS_LOG',
        action='store_true',
        default=False,
        help='Print flows to console.',
    )
    case_group.add_option(
        '--step-by-step',
        dest='STEP_BY_STEP',
        action='store_true',
        default=False,
        help='Do prompt before run test step.',
    )
    parser.add_option_group(case_group)

    run_group = OptionGroup(parser, 'Run options')
    run_group.add_option(
        '-t', '--test',
        action='append',
        dest='TESTS',
        default=[],
        help='Run these tests.',
    )
    run_group.add_option(
        '--include-regexp',
        dest='INCLUDE_SUITES_PATTERN',
        type=str,
        default=None,
        help='Regexp for allow registration suite by name.',
    )
    run_group.add_option(
        '--exclude-regexp',
        dest='EXCLUDE_SUITE_PATTERN',
        type=str,
        default=None,
        help='Regexp for not allow registration suite by name.',
    )
    run_group.add_option(
        '-x', '--stop',
        dest='STOP',
        action='store_true',
        default=False,
        help='Stop running tests after the first error or failure.',
    )
    run_group.add_option(
        '-r', '--repeat',
        dest='REPEAT',
        type=int,
        default=0,
        help='Num of tries to repeat test',
    )
    run_group.add_option(
        '--random',
        dest='RANDOM',
        action='store_true',
        default=False,
        help='Random order when tests is running.',
    )
    run_group.add_option(
        '--random-seed',
        dest='RANDOM_SEED',
        default=time.time(),
        help='Seed for random tests and suites.',
    )
    run_group.add_option(
        '--no-skip',
        dest='NO_SKIP',
        action='store_true',
        default=False,
        help='Disable special handling of SkipTest exceptions.',
    )
    run_group.add_option(
        '--no-scripts',
        dest='NO_SCRIPTS',
        action='store_true',
        default=False,
        help='Ignore scripts on run.',
    )
    run_group.add_option(
        '--async-suites',
        type=int,
        dest='ASYNC_SUITES',
        default=0,
        help='Num suites to async run.',
    )
    run_group.add_option(
        '--async-tests',
        type=int,
        dest='ASYNC_TESTS',
        default=0,
        help='Num tests from suite to async run.',
    )
    run_group.add_option(
        '--mp-timeout',
        type=float,
        dest='MULTIPROCESSING_TIMEOUT',
        default=float(1800),
        help='Timeout to release and join multiprocessing process.',
    )
    run_group.add_option(
        '--gevent',
        dest='GEVENT',
        action='store_true',
        default=False,
        help='Use gevent groups for run. Allow for python 2 only.',
    )
    run_group.add_option(
        '--threading',
        dest='THREADING',
        action='store_true',
        default=False,
        help='Use threading groups for run.',
    )
    run_group.add_option(
        '--multiprocessing',
        dest='MULTIPROCESSING',
        action='store_true',
        default=False,
        help='Use multiprocessing groups for run.',
    )
    parser.add_option_group(run_group)

    return parser


def prepare_config(config):
    logging_settings = config.get('LOGGING_SETTINGS')

    if isinstance(logging_settings, dict):
        from logging.config import dictConfig
        dictConfig(logging_settings)

    if not config.GEVENT and not config.THREADING and (
            config.ASYNC_SUITES or config.ASYNC_TESTS):
        config.MULTIPROCESSING = True

    if (config.STEPS_LOG or config.FLOWS_LOG) and not config.VERBOSE:
        config.VERBOSE = True


def get_config_path_by_env(env_name, default=None, base_path=None):
    config_path = os.getenv(env_name, default)

    if base_path and config_path:
        config_path = '{}{}'.format(base_path, config_path)

    return config_path


def _load(obj, load_callable=True):
    def is_valid(atr):
        if load_callable:
            condition = not atr.startswith('_')
        else:
            condition = not atr.startswith('_') \
                and \
                not callable(getattr(obj, atr, None))

        return condition

    for atr in dir(obj):
        if is_valid(atr):
            yield (atr, getattr(obj, atr))


class Config(DictObject):

    def __init__(self, path=None, options=None):
        super(Config, self).__init__()

        if path:
            def is_import_path():
                is_dot_in_path = '.' in path
                is_py_ex = path.endswith('.py')

                return is_dot_in_path and not is_py_ex

            if is_import_path():
                self.from_module(path)
            elif path.endswith('.py'):
                self.from_py_file(path)

        if options:
            self.update(
                _load(options, load_callable=False)
            )

    def from_module(self, module):
        logger.debug(
            'Init config from module "{}"'.format(module),
        )

        try:
            obj = import_module(module)
        except ImportError:
            raise ImportError('Config {} not found'.format(module))

        self.update(_load(obj))

        return self

    def from_py_file(self, file_path):
        logger.debug(
            'Init config from py file "{}"'.format(file_path),
        )

        if not os.path.isfile(file_path):
            raise ConfigError(
                'config file does not exist at path "{}"'.format(file_path),
            )

        elif not file_path.endswith('.py'):
            raise ConfigError(
                'config file is not python file',
            )

        module = imp.new_module(file_path.rstrip('.py'))
        module.__file__ = file_path

        try:
            pyv.execfile(file_path, module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load file "{}"'.format(e.strerror)
            raise

        self.update(_load(module))

        return self
