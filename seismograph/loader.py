# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from random import randint
from importlib import import_module

from .exceptions import LoaderError


logger = logging.getLogger(__name__)


TEST_NAME_PREFIX = 'test'
DEFAULT_TEST_NAME = 'test'

TASK_NAME_PREFIX = 'task'


def check_path_is_exist(path):
    if not os.path.exists(path):
        raise LoaderError('Dir "{}" is not exist'.format(path))


def is_package(path):
    return os.path.isfile(
        os.path.join(path, '__init__.py'),
    )


def is_py_module(file_name):
    return not file_name.startswith('_') \
        and file_name.endswith('.py')


def load_module(module_name, package=None):
    module_name = '{}{}'.format(
        package + '.' if package else '', module_name,
    )

    logger.debug('Load module "{}"'.format(module_name))

    module = import_module(module_name)

    load_session = str(time.time() + randint(0, 1000))
    system_name = '{}_{}'.format(module_name, load_session)

    del sys.modules[module_name]
    sys.modules[system_name] = module

    return module


def load_test_names_from_case(
        cls,
        test_name_prefix=None,
        default_test_name=None):
    def is_test_name(name):
        return name.startswith((test_name_prefix or TEST_NAME_PREFIX)) \
            or \
            name == (default_test_name or DEFAULT_TEST_NAME)

    for name in sorted(dir(cls)):
        if is_test_name(name):
            logger.debug(
                'Load test "{}" from case "{}.{}"'.format(
                    name, cls.__module__, cls.__name__,
                ),
            )
            yield name


def load_tests_from_case(
        cls,
        config=None,
        box_class=None,
        method_name=None,
        test_name_prefix=None,
        default_test_name=None):
    logger.debug(
        'Load test from case "{}.{}"'.format(
            cls.__module__, cls.__name__,
        ),
    )

    cls_tag = getattr(cls, '__tag__', None)

    if (config and config.TAGS) and (cls_tag not in config.TAGS):
        raise StopIteration

    if method_name:
        for name in filter(lambda n: n == method_name, dir(cls)):
            case = cls(name, config=config)
            if box_class:
                yield box_class((case, ))
            else:
                yield case
            raise StopIteration
        else:
            raise LoaderError(
                'Test "{}" not found in "{}"'.format(
                    method_name, cls.__name__,
                ),
            )
    else:
        names = load_test_names_from_case(
            cls,
            test_name_prefix=(test_name_prefix or TEST_NAME_PREFIX),
            default_test_name=(default_test_name or DEFAULT_TEST_NAME),
        )

        if box_class:
            cases = []

            for name in names:
                cases.append(
                    cls(name, config=config)
                )

            yield box_class(cases)
        else:
            for name in names:
                yield cls(name, config=config)


def load_suite_by_name(name, suites):
    logger.debug(
        'Load suite "{}" from list'.format(name),
    )

    for suite in filter(lambda s: s.name == name, suites):
        return suite
    else:
        raise LoaderError(
            'Suite "{}" not found'.format(name),
        )


def load_case_from_suite(class_name, suite):
    logger.debug(
        'Load case "{}" from suite "{}"'.format(
            class_name, suite.name,
        ),
    )

    for case_cls in filter(lambda c: c.__name__ == class_name, suite.cases):
        return case_cls
    else:
        raise LoaderError(
            'Test case "{}" not found'.format(class_name),
        )


def load_suites_from_module(module, suite_class):
    logger.debug(
        'Load suite from module {} by class "{}.{}"'.format(
            module, suite_class.__module__, suite_class.__name__,
        ),
    )

    for attribute in dir(module):
        value = getattr(module, attribute, None)
        if isinstance(value, suite_class):
            yield value


def load_suites_from_path(path_to_dir, suite_class, package=None, recursive=True):
    logger.debug(
        'Load suites from path "{}"'.format(path_to_dir),
    )

    check_path_is_exist(path_to_dir)

    lst_dir = os.listdir(path_to_dir)
    full_path = lambda *n: os.path.join(path_to_dir, *n)

    modules = (n.replace('.py', '') for n in lst_dir if is_py_module(n))

    for module_name in modules:
        module = load_module(module_name, package=package)

        for suite in load_suites_from_module(module, suite_class):
            yield suite

    if recursive:
        packs = (n for n in lst_dir if is_package(full_path(n)))

        for pack in packs:

            for suite in load_suites_from_path(
                    full_path(pack),
                    suite_class,
                    recursive=recursive,
                    package='{}.{}'.format(package, pack) if package else pack):
                yield suite


def load_separated_classes_for_flows(case_cls):
    if not case_cls.__flows__ or not isinstance(case_cls.__flows__, (list, tuple)):
        return [case_cls]

    new_classes = []

    for flow in case_cls.__flows__:
        index = case_cls.__flows__.index(flow)
        new_class_name = '{}{}'.format(case_cls.__name__, (index + 1))

        cls = type(
            new_class_name,
            (case_cls, ),
            {
                '__flows__': (flow, ),
            },
        )

        new_classes.append(cls)

    return new_classes


def load_tasks_from_script(program, script, task_name_prefix=None):
    task_name_prefix = task_name_prefix or TASK_NAME_PREFIX
    task_names = (n for n in dir(script) if n.startswith(task_name_prefix))

    for task_name in task_names:
        yield script(program, task_name)
