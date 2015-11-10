# -*- coding: utf-8 -*-

from optparse import OptionGroup

from ...extensions import BaseExtension

from .selenium import EX_NAME
from .selenium import Selenium
from .selenium import assertion
from .selenium import inject_driver
from .selenium import case_of_browsers
from .selenium import SeleniumAssertion
from .selenium import SeleniumCase as Case
from .selenium import SeleniumSuite as Suite

from . import forms

from .query import QueryObject

from .router import add_route

from .page_object import Page
from .page_object import PageObject
from .page_object import PageObjectProxy


query = QueryObject


class SeleniumExtension(BaseExtension):

    __ex_name__ = EX_NAME
    __config_key__ = 'SELENIUM_EX'

    @staticmethod
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

    def __install__(self, program):
        config = program.config.get(self.__config_key__, {})

        if program.config.SELENIUM_PROJECT_URL:
            config['PROJECT_URL'] = program.config.SELENIUM_PROJECT_URL

        if program.config.SELENIUM_POLLING:
            config['POLLING_TIMEOUT'] = program.config.SELENIUM_POLLING

        if program.config.SELENIUM_WINDOW_SIZE:
            w, h = program.config.SELENIUM_WINDOW_SIZE.split('x')
            config['WINDOW_SIZE'] = (int(w), int(h))

        program.shared_extension(
            self.__ex_name__, Selenium, args=(config, ),
        )

    def __call__(self):
        raise TypeError(
            '"{}" is not callable'.format(
                self.__class__.__name__,
            ),
        )


__all__ = (
    'Case',
    'Page',
    'forms',
    'query',
    'Suite',
    'Selenium',
    'add_route',
    'assertion',
    'PageObject',
    'QueryObject',
    'inject_driver',
    'PageObjectProxy',
    'case_of_browsers',
    'SeleniumAssertion',
)
