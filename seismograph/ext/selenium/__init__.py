# -*- coding: utf-8 -*-

from optparse import OptionGroup

from . import forms
from .query import contains
from .pageobject import Page
from .router import add_route
from .query import QueryObject
from .extension import assertion
from .pageobject import PageObject
from .extension import inject_driver
from .pageobject import PageObjectProxy
from .extension import case_of_browsers
from .extension import SeleniumAssertion
from .extension import SeleniumCase as Case
from .extension import SeleniumSuite as Suite


CONFIG_KEY = 'SELENIUM_EX'


def __add_options__(parser):
    group = OptionGroup(parser, 'Selenium extension options')

    group.add_option(
        '--selenium-browser',
        dest='SELENIUM_BROWSERS',
        action='append',
        default=[],
        help='Browser names for run cases.',
    )
    group.add_option(
        '--selenium-project-url',
        dest='SELENIUM_PROJECT_URL',
        default=None,
        help='Base URL of your project.',
    )
    group.add_option(
        '--selenium-no-remote',
        dest='SELENIUM_NO_REMOTE',
        action='store_true',
        default=False,
        help='Use local drivers only.'
    )
    group.add_option(
        '--selenium-polling',
        dest='SELENIUM_POLLING',
        type=float,
        default=None,
        help='Polling timeout.',
    )
    group.add_option(
        '--selenium-window-size',
        dest='SELENIUM_WINDOW_SIZE',
        default=None,
        help='Window size. For example: 340x480',
    )

    parser.add_option_group(group)


def __install__(program):
    from .extension import EX_NAME
    from .extension import Selenium

    config = program.config.get(CONFIG_KEY, {})

    if program.config.SELENIUM_PROJECT_URL:
        config['PROJECT_URL'] = program.config.SELENIUM_PROJECT_URL

    if program.config.SELENIUM_NO_REMOTE:
        config['USE_REMOTE'] = False

    if program.config.SELENIUM_POLLING:
        config['POLLING_TIMEOUT'] = program.config.SELENIUM_POLLING

    if program.config.SELENIUM_WINDOW_SIZE:
        w, h = program.config.SELENIUM_WINDOW_SIZE.split('x')
        config['WINDOW_SIZE'] = (int(w), int(h))

    program.shared_extension(
        EX_NAME, Selenium, args=(config, ),
    )


query = QueryObject


__all__ = (
    'Case',
    'Page',
    'forms',
    'query',
    'Suite',
    'contains',
    'add_route',
    'assertion',
    'PageObject',
    'QueryObject',
    'inject_driver',
    'PageObjectProxy',
    'case_of_browsers',
    'SeleniumAssertion',
)
