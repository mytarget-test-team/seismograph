# -*- coding: utf-8 -*-

import logging
from random import Random

from . import loader
from . import extensions
from .suite import BuildRule
from .exceptions import CollectError
from .utils.common import call_to_chain


logger = logging.getLogger(__name__)


def get_shuffle(config):
    if config.RANDOM:
        random = Random(config.RANDOM_SEED)
        return random.shuffle
    return None


def get_suite_name_from_command(command):
    try:
        suite_name, _ = command.split(':')
    except ValueError:
        return command

    return suite_name


def get_case_name_from_command(command):
    try:
        _, case_name = command.split(':')
        try:
            case_name, test_name = case_name.split('.')
        except ValueError:
            pass
        return case_name
    except ValueError:
        return None


def get_test_name_from_command(command):
    try:
        _, case_name = command.split(':')
        try:
            _, test_name = case_name.split('.')
            return test_name
        except ValueError:
            return None
    except ValueError:
        return None


def try_apply_rules(suite, rules):
    for rule in rules[::-1]:
        if rule.is_of(suite):
            suite.assign_build_rule(rule)
            rules.remove(rule)


def base_generator(suites, shuffle=None):
    call_to_chain(suites, 'build', shuffle=shuffle)
    extensions.clear()

    if shuffle:
        shuffle(suites)

    for suite in suites:
        yield suite


def generator_by_commands(suites, rules, shuffle=None):
    loaded_suites = []

    for rule in rules[::-1]:
        suite = loader.load_suite_by_name(rule.suite_name, suites)

        try_apply_rules(suite, rules)
        if suite not in loaded_suites:
            loaded_suites.append(suite)

    if rules:
        raise CollectError(
            'incorrect commands to collect "{}"'.format(
                ', '.join(str(r) for r in rules),
            ),
        )

    call_to_chain(loaded_suites, 'build', shuffle=shuffle)
    extensions.clear()

    if shuffle:
        shuffle(loaded_suites)

    for suite in loaded_suites:
        yield suite


def create_generator(suites, config):
    if config.TESTS:
        logger.debug('Create suite generator by commands')

        rules = [
            BuildRule(
                suite_name=get_suite_name_from_command(c),
                case_name=get_case_name_from_command(c),
                test_name=get_test_name_from_command(c),
            )
            for c in config.TESTS
        ]
        return generator_by_commands(
            suites, rules, shuffle=get_shuffle(config),
        )

    logger.debug('Create base suite generator')

    return base_generator(
        suites, shuffle=get_shuffle(config),
    )
