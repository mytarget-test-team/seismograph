# -*- coding: utf-8 -*-

import logging

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from ...utils.common import waiting_for
from ...exceptions import TimeoutException
from .utils import change_name_from_python_to_html


logger = logging.getLogger(__name__)


TAG_ALIASES = {
    'link': 'a',
}
ATTRIBUTE_ALIASES = {
    '_id': 'id',
    '_class': 'class',
    '_type': 'type',
}


class QueryObject(object):

    def __init__(self, tag, **selector):
        self.tag = tag
        self.selector = selector

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'<{} {}>'.format(
            self.tag,
            u' '.join(
                (u'{}="{}"'.format(k, v) for k, v in self.selector.items())
            ),
        )


class _Contains(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return unicode(self.value)


contains = _Contains


def tag_by_alias(tag_name):
    return TAG_ALIASES.get(tag_name, tag_name)


def attribute_by_alias(atr_name):
    return change_name_from_python_to_html(
        ATTRIBUTE_ALIASES.get(atr_name, atr_name),
    )


def make_result(proxy, tag):
    def handle(**selector):
        query = [tag_by_alias(tag)]

        def get_format(value):
            if isinstance(value, contains):
                return u'[{}*="{}"]'
            return u'[{}="{}"]'

        query.extend(
            (
                get_format(val).format(attribute_by_alias(atr), val)
                for atr, val in selector.items()
            ),
        )

        return QueryResult(proxy, ''.join(query))

    return handle


def get_execute_method(proxy, can_many):
    css_executors = {
        True: 'find_elements_by_css_selector',
        False: 'find_element_by_css_selector',
    }
    method_name = css_executors[bool(can_many)]

    return getattr(proxy, method_name)


def execute(proxy, css, can_many=False, disable_polling=False):
    logger.debug(u'CSS: {} Can many: {}'.format(css, 'Yes' if can_many else 'No'))

    proxy.reason_storage['last css query'] = css

    if disable_polling:
        with proxy.disable_polling():
            method = get_execute_method(proxy, can_many)
            return method(css)

    method = get_execute_method(proxy, can_many)
    return method(css)


class QueryResult(object):

    def __init__(self, proxy, css):
        self.__proxy = proxy
        self.__css = css

    def __getattr__(self, item):
        obj = self.first()
        return getattr(obj.query, item)

    @property
    def exist(self):
        try:
            el = execute(self.__proxy, self.__css, disable_polling=True)

            if el:
                return True
            return False
        except WebDriverException:
            return False

    def wait(self, timeout=None):
        try:
            return waiting_for(
                lambda: self.exist,
                timeout=timeout or self.__proxy.config.POLLING_TIMEOUT,
            )
        except TimeoutException:
            raise TimeoutException(
                'Could not wait web element with css "{}"'.format(self.__css),
            )

    def get(self, index):
        try:
            return execute(self.__proxy, self.__css, can_many=True)[index]
        except IndexError:
            raise NoSuchElementException(
                'Result does not have element with index "{}". Css: "{}".'.format(
                    index, self.__css,
                ),
            )

    def first(self):
        return execute(self.__proxy, self.__css)

    def all(self):
        return execute(self.__proxy, self.__css, can_many=True)


class QueryProcessor(object):

    def __init__(self, proxy):
        self.__proxy = proxy

    def __getattr__(self, item):
        return make_result(self.__proxy, item)

    def __call__(self, proxy):
        return self.__class__(proxy)

    @property
    def proxy(self):
        return self.__proxy

    @property
    def driver(self):
        return self.__proxy.driver

    def from_object(self, obj):
        if not isinstance(obj, QueryObject):
            raise TypeError('"{}" is not QueryObject instance'.format(type(obj)))

        return self.__getattr__(obj.tag)(**obj.selector)
