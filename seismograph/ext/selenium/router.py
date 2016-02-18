# -*- coding: utf-8 -*-

import re

from .exceptions import RouterError
from .exceptions import RouteNotFound


def add_route(rule, cls):
    Router.add_rule(rule, cls)


class Router(object):

    __rules__ = {}

    def __init__(self, proxy):
        self.__proxy = proxy

    @classmethod
    def add_rule(cls, rule, class_):
        cls.__rules__[re.compile(r'^{}$'.format(rule))] = class_

    def get(self, path, go_to=True):
        for rule in self.__rules__:
            if rule.search(path) is not None:
                cls = self.__rules__[rule]
                page = cls(self.__proxy)
                break
        else:
            raise RouteNotFound(path)

        if go_to:
            self.go_to(path)

        return page

    def get_page(self, path):
        return self.get(path, go_to=False)

    def go_to(self, path):
        if not self.__proxy.config.PROJECT_URL:
            raise RouterError(
                'Can not go to the URL. Project URL is not set to config.',
            )

        self.__proxy.browser.get(
            '{}{}'.format(
                self.__proxy.config.PROJECT_URL.strip('/'), path,
            ),
        )
