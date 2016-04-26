# -*- coding: utf-8 -*-

from warnings import warn
from optparse import OptionGroup

from . import forms
from . import polling

from .case import assertion
from .case import require_browser
from .case import SeleniumAssertion
from .case import make_with_browsers
from .case import SeleniumCase as Case

from .suite import SeleniumSuite as Suite

from .proxy.actions import Alert
from .proxy.actions import ActionChains
from .proxy.actions import TouchActions

from .pageobject import Page
from .pageobject import PageItem
from .pageobject import PageElement

from .query import query

from .router import add_route

from .utils import re_raise_exc

from .browser import change_config as change_browser_config


CONFIG_KEY = 'SELENIUM_EX'


def __add_options__(parser):
    group = OptionGroup(parser, 'Selenium extension options')

    group.add_option(
        '--selenium-browser',
        dest='SELENIUM_BROWSERS',
        action='append',
        default=[],
        help='Browser name for run cases.',
    )
    group.add_option(
        '--selenium-project-url',
        dest='SELENIUM_PROJECT_URL',
        default=None,
        help='Base URL of your project.',
    )
    group.add_option(
        '--selenium-remote',
        dest='SELENIUM_REMOTE',
        action='store_true',
        default=False,
        help='Use remote server only.'
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
        help='Polling timeout. Float or integer value.',
    )
    group.add_option(
        '--selenium-polling-delay',
        dest='SELENIUM_POLLING_DELAY',
        type=float,
        default=None,
        help='Polling delay. Float or integer value.',
    )
    group.add_option(
        '--selenium-wait-timeout',
        dest='SELENIUM_WAIT_TIMEOUT',
        type=float,
        default=None,
        help='Implicitly wait timeout. Float or integer value.',
    )
    group.add_option(
        '--selenium-page-load-timeout',
        dest='SELENIUM_PAGE_LOAD_TIMEOUT',
        type=float,
        default=None,
        help='Load page timeout. Float or integer value.',
    )
    group.add_option(
        '--selenium-script-timeout',
        dest='SELENIUM_SCRIPT_TIMEOUT',
        type=float,
        default=None,
        help='Execute script timeout. Float or integer value.',
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

    if program.config.SELENIUM_REMOTE:
        config['USE_REMOTE'] = True

    if program.config.SELENIUM_POLLING:
        config['POLLING_TIMEOUT'] = program.config.SELENIUM_POLLING

    if program.config.SELENIUM_POLLING_DELAY:
        config['POLLING_DELAY'] = program.config.SELENIUM_POLLING_DELAY

    if program.config.SELENIUM_WAIT_TIMEOUT:
        config['WAIT_TIMEOUT'] = program.config.SELENIUM_WAIT_TIMEOUT

    if program.config.SELENIUM_PAGE_LOAD_TIMEOUT:
        config['PAGE_LOAD_TIMEOUT'] = program.config.SELENIUM_PAGE_LOAD_TIMEOUT

    if program.config.SELENIUM_SCRIPT_TIMEOUT:
        config['SCRIPT_TIMEOUT'] = program.config.SELENIUM_SCRIPT_TIMEOUT

    if program.config.SELENIUM_WINDOW_SIZE:
        w, h = program.config.SELENIUM_WINDOW_SIZE.split('x')
        config['WINDOW_SIZE'] = (int(w), int(h))

    if (config.get('POLLING_TIMEOUT') and config.get('IMPLICITLY_WAIT')) \
            and config.get('POLLING_TIMEOUT') >= config.get('IMPLICITLY_WAIT'):
        warn_message = 'POLLING_TIMEOUT >= IMPLICITLY_WAIT it will be working so slowly. ' \
                       'Please set IMPLICITLY_WAIT larger POLLING_TIMEOUT'
        warn(warn_message, RuntimeWarning)

    program.shared_extension(
        EX_NAME, Selenium, args=(config, ),
    )


__all__ = (
    'Case',
    'Page',
    'forms',
    'query',
    'Alert',
    'Suite',
    'polling',
    'PageItem',
    'add_route',
    'assertion',
    'waiting_for',
    'PageElement',
    'ActionChains',
    'TouchActions',
    're_raise_exc',
    'inject_driver',
    'SeleniumAssertion',
    'make_with_browsers',
    'change_browser_config',
)
