# -*- coding: utf-8 -*-

import re
import sys
import logging
import traceback

from . import ext
from . import config
from . import loader
from . import runnable
from .utils import pyv
from . import collector
from . import extensions
from .suite import Suite
from .result import Result
from .utils.common import measure_time
from .utils.common import call_to_chain
from .groups.default import DefaultSuiteGroup
from .exceptions import ALLOW_RAISED_EXCEPTIONS


logger = logging.getLogger(__name__)


DEFAULT_LAYERS = []
CONFIG_ENV_NAME = 'SEISMOGRAPH_CONF'


class ProgramLayer(runnable.LayerOfRunnableObject):

    def on_init(self, program):
        """
        :type program: Program
        """
        pass

    def on_config(self, config):
        """
        :type config: seismograph.config.Config
        """
        pass

    def on_setup(self, program):
        """
        :type program: Program
        """
        pass

    def on_teardown(self, program):
        """
        :type program: Program
        """
        pass

    def on_error(self, error, program, result):
        """
        :type error: BaseException
        :type program: Program
        :type result: seismograph.result.Result
        """
        pass

    def on_option_parser(self, parser):
        """
        :param parser: optparse.OptionParser
        """
        pass

    def on_run(self, program):
        """
        :type program: Program
        """
        pass


class ProgramContext(runnable.ContextOfRunnableObject):

    def __init__(self, setup, teardown):
        self.__layers = []

        self.__setup_callbacks = [setup]
        self.__teardown_callbacks = [teardown]

    @property
    def setup_callbacks(self):
        return self.__setup_callbacks

    @property
    def teardown_callbacks(self):
        return self.__teardown_callbacks

    @property
    def layers(self):
        for layer in DEFAULT_LAYERS:
            if layer.enabled:
                yield layer

        for layer in self.__layers:
            if layer.enabled:
                yield layer

    def add_layers(self, layers):
        self.__layers.extend(layers)

    def start_context(self, program):
        logger.debug(
            'Start context of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        try:
            call_to_chain(self.layers, 'on_setup', program)
            call_to_chain(self.__setup_callbacks, None)
        except BaseException:
            runnable.stopped_on(program, 'start_context')
            raise

    def stop_context(self, program):
        logger.debug(
            'Stop context of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        try:
            call_to_chain(self.layers, 'on_teardown', program)
            call_to_chain(self.__teardown_callbacks, None)
        except BaseException:
            runnable.stopped_on(program, 'stop_context')
            raise

    def on_init(self, program):
        logger.debug(
            'Call to chain callbacks "on_init" of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        call_to_chain(self.layers, 'on_init', program)

    def on_config(self, program, config):
        logger.debug(
            'Call to chain callbacks "on_config" of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        call_to_chain(self.layers, 'on_config', config)

    def on_error(self, error, program, result):
        logger.debug(
            'Call to chain callbacks "on_error" of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        try:
            call_to_chain(self.layers, 'on_error', error, program, result)
        except BaseException:
            runnable.stopped_on(program, 'on_error')
            raise

    def on_option_parser(self, parser):
        logger.debug(
            'Call to chain callbacks "on_option_parser" of program',
        )

        call_to_chain(self.layers, 'on_option_parser', parser)

    def on_run(self, program):
        logger.debug(
            'Call to chain callbacks "on_run" of program "{}"'.format(
                runnable.class_name(program),
            ),
        )

        try:
            call_to_chain(self.layers, 'on_run', program)
        except BaseException:
            runnable.stopped_on(program, 'on_run')
            raise


class Program(runnable.RunnableObject):

    __layers__ = None
    __suite_class__ = Suite
    __create_reason__ = False
    __result_class__ = Result
    __suite_group_class__ = None
    __config_class__ = config.Config

    #
    # Base components of runnable object
    #

    def __is_run__(self):
        return self.__is_run

    def __run__(self):
        self.__is_run = True
        timer = measure_time()
        self.__result.set_timer(timer)

        if self.suites_path:
            self.load_suites()

        if not self.__suites and not self.__scripts:
            raise RuntimeError(
                'No suites or scripts for execution',
            )

        self.__suites = collector.create_generator(
            self.__suites, self.__config,
        )

        if self.__config.TREE:
            from .tree import print_tree
            print_tree(self.__suites)

        group = self._make_group()

        with self.__result:
            try:
                self.__context.on_run(self)

                with self.__context(self):
                    self.run_scripts(run_point='before')
                    group(self.__result)
                    self.run_scripts(run_point='after')
                    self.__result.stop_timer()
            except ALLOW_RAISED_EXCEPTIONS:
                raise
            except BaseException as error:
                self.__context.on_error(error, self, self.__result)
                self.__result.add_error(
                    self, traceback.format_exc(), timer(), error,
                )

        if self.__exit:
            sys.exit(not self.__result.current_state.was_success)

        return self.__result.current_state.was_success

    #
    # Self code is starting here
    #

    def __init__(self,
                 suites_path='__main__',
                 recursive_load=True,
                 scripts=None,
                 config_path=None,
                 layers=None,
                 argv=None,
                 exit=True,
                 stream=None,
                 suites=None):
        super(Program, self).__init__()

        if argv:
            sys.argv.extend(argv)

        self.suites_path = suites_path
        self.recursive_load = recursive_load

        self.__suites = []
        self.__scripts = []
        self.__exit = exit
        self.__is_run = False
        self.__stream = stream

        self.__context = ProgramContext(self.setup, self.teardown)

        if self.__layers__:
            self.__context.add_layers(self.__layers__)

        if layers:
            self.__context.add_layers(layers)

        parser = config.create_option_parser()
        self.__context.on_option_parser(parser)

        for extension in ext.TO_INIT:
            extensions.add_options(extension, parser)

        options, _ = parser.parse_args()

        self.__config = self.__config_class__(
            config.get_config_path_by_env(
                CONFIG_ENV_NAME, default=config_path,
            ),
            options=options,
        )

        config.prepare_config(self.__config)

        self.__result = self._make_result()

        self.__context.on_config(self, self.__config)

        if self.__config.NO_SKIP:
            from .case import set_no_skip
            set_no_skip()

        for extension in ext.TO_INIT:
            extensions.install(extension, self)

        if suites:
            self.register_suites(suites)

        if scripts:
            self.register_scripts(scripts)

        self.__context.on_init(self)

    @property
    def exit(self):
        return self.__exit

    @exit.setter
    def exit(self, value):
        self.__exit = value

    @property
    def suites(self):
        return self.__suites

    @property
    def config(self):
        return self.__config

    @property
    def context(self):
        return self.__context

    @property
    def scripts(self):
        return self.__scripts

    def _make_group(self):
        if self.__suite_group_class__:
            logger.debug(
                'Use "__suite_group_class__" to making suite group',
            )

            return self.__suite_group_class__(
                self.__suites, self.__config,
            )

        if self.config.GEVENT:
            logger.debug(
                'Use "GeventSuiteGroup" to making suite group',
            )

            pyv.check_gevent_supported()

            from .groups.gevent import GeventSuiteGroup

            return GeventSuiteGroup(
                self.__suites, self.__config,
            )

        if self.config.THREADING:
            logger.debug(
                'Use "ThreadingSuiteGroup" to making suite group',
            )

            from .groups.threading import ThreadingSuiteGroup

            return ThreadingSuiteGroup(
                self.__suites, self.__config,
            )

        if self.config.MULTIPROCESSING:
            logger.debug(
                'Use "MultiprocessingSuiteGroup" to making suite group',
            )

            from .groups.multiprocessing import MultiprocessingSuiteGroup

            return MultiprocessingSuiteGroup(
                self.__suites, self.__config,
            )

        logger.debug(
            'Use "DefaultSuiteGroup" to making suite group',
        )

        return DefaultSuiteGroup(
            self.__suites, self.__config,
        )

    def _make_result(self):
        if self.__config.OUTPUT:
            stream = open(self.__config.OUTPUT, 'w')
            logger.info(
                'Result output stream was redirected to "{}"'.format(
                    self.__config.OUTPUT,
                ),
            )
        elif self.__stream:
            stream = self.__stream
        else:
            stream = sys.stdout

        return self.__result_class__(
            self.__config,
            stream=stream,
        )

    @staticmethod
    def ext(name):
        return extensions.get(name)

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

    @staticmethod
    def shared_data(name, data):
        extensions.set(data, name, is_data=True)

    @staticmethod
    def shared_extension(name, ext, singleton=False, args=None, kwargs=None):
        extensions.set(
            ext,
            name,
            is_data=False,
            singleton=singleton,
            args=args, kwargs=kwargs,
        )

    def suite_is_valid(self, suite):
        is_valid = True

        if self.__config.INCLUDE_SUITES_PATTERN:
            is_valid = bool(
                re.search(self.__config.INCLUDE_SUITES_PATTERN, suite.name),
            )

        if self.__config.EXCLUDE_SUITE_PATTERN:
            is_valid = not bool(
                re.search(self.__config.EXCLUDE_SUITE_PATTERN, suite.name),
            )

        return is_valid

    def register_scripts(self, scripts):
        for script in scripts:
            self.register_script(script)

    def register_script(self, script, run_point=None):
        if not self.__config.NO_SCRIPTS:
            if run_point:
                setattr(script, '__run_point__', run_point)
            self.__scripts.append(script(self))

    def register_suite(self, suite):
        if self.suite_is_valid(suite):
            logger.debug(
                'Register suite "{}" on program "{}"'.format(
                    suite.name, runnable.class_name(self),
                ),
            )
            suite.mount_to(self)

    def register_suites(self, suites):
        for suite in suites:
            self.register_suite(suite)

    def load_suites(self, path=None):
        path = path or self.suites_path

        if path:
            if path == '__main__':
                self.register_suites(
                    loader.load_suites_from_module(
                        __import__('__main__'),
                        self.__suite_class__,
                    ),
                )
            else:
                if path not in sys.path:
                    sys.path.append(path)

                self.register_suites(
                    loader.load_suites_from_path(
                        path,
                        self.__suite_class__,
                        recursive=self.recursive_load,
                    ),
                )

    def run_scripts(self, result=None, run_point=None):
        if run_point:
            scripts = filter(
                lambda s: s.__run_point__ == run_point, self.__scripts,
            )
        else:
            scripts = self.__scripts

        if result is None:
            result = self.__result

        for script in scripts:
            with result.proxy(script) as result_proxy:
                script(result_proxy)
            if result.current_state.should_stop:
                break


def main(*args, **kwargs):
    runnable.run(
        Program(*args, **kwargs),
    )
