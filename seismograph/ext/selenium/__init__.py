# -*- coding: utf-8 -*-

from warnings import warn
from optparse import OptionGroup

from . import forms
from .pageobject import Page
from .router import add_route
from .utils import re_raise_exc
from .extension import assertion
from .pageobject import PageObject
from .extension import inject_driver
from .pageobject import PageObjectProxy
from .extension import case_of_browsers
from .extension import SeleniumAssertion
from .query import Contains as _Contains
from .extension import SeleniumCase as Case
from .extension import SeleniumSuite as Suite
from .query import QueryObject as _QueryObject


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
        help='Polling timeout.',
    )
    group.add_option(
        '--selenium-polling-delay',
        dest='SELENIUM_POLLING_DELAY',
        type=float,
        default=None,
        help='Polling delay.',
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

    if program.config.SELENIUM_WINDOW_SIZE:
        w, h = program.config.SELENIUM_WINDOW_SIZE.split('x')
        config['WINDOW_SIZE'] = (int(w), int(h))

    if (config['POLLING_TIMEOUT'] and config['IMPLICITLY_WAIT']) \
            and config['POLLING_TIMEOUT'] >= config['IMPLICITLY_WAIT']:
        warn_message = 'POLLING_TIMEOUT >= IMPLICITLY_WAIT it will be work so slowly. ' \
                       'Please set IMPLICITLY_WAIT larger POLLING_TIMEOUT'
        warn(warn_message, RuntimeWarning)

    program.shared_extension(
        EX_NAME, Selenium, args=(config, ),
    )


class _Query(object):
    """
    For usability only.

    query('div', _class=query.contains('name'))
    """

    @property
    def contains(self):
        return _Contains

    def __call__(self, tag, **selector):
        return _QueryObject(tag, **selector)


query = _Query()


__all__ = (
    'Case',
    'Page',
    'forms',
    'query',
    'Suite',
    'add_route',
    'assertion',
    'PageObject',
    're_raise_exc',
    'inject_driver',
    'PageObjectProxy',
    'case_of_browsers',
    'SeleniumAssertion',
)
