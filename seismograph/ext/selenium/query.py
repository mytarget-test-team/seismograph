# -*- coding: utf-8 -*-

import logging

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from ...utils import pyv
from ...utils.common import waiting_for
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

    def __call__(self, proxy):
        return make_result(proxy, self.tag)(**self.selector)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'<{} {}>'.format(
            self.tag,
            u' '.join(
                (u'{}="{}"'.format(k, v) for k, v in self.selector.items())
            ),
        )


class Contains(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return unicode(self.value)


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
            if isinstance(value, Contains):
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


def get_execute_method(proxy, list_result):
    css_executors = {
        True: 'find_elements_by_css_selector',
        False: 'find_element_by_css_selector',
    }
    method_name = css_executors[bool(list_result)]

    return getattr(proxy, method_name)


def execute(proxy, css, list_result=False, disable_polling=False):
    logger.debug(
        u'Execute css query "{}", list result "{}"'.format(
            css, 'Yes' if list_result else 'No',
        ),
    )

    proxy.reason_storage['last css query'] = css

    if disable_polling:
        with proxy.disable_polling():
            method = get_execute_method(proxy, list_result)
            return method(css)

    method = get_execute_method(proxy, list_result)
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
        return waiting_for(
            lambda: self.exist,
            exc_cls=NoSuchElementException,
            timeout=timeout or self.__proxy.config.POLLING_TIMEOUT,
            message='Could not wait web element by css "{}"'.format(self.__css),
        )

    def get(self, index):
        try:
            return execute(self.__proxy, self.__css, list_result=True)[index]
        except IndexError:
            raise NoSuchElementException(
                'Result does not have element with index "{}". Css query: "{}".'.format(
                    index, self.__css,
                ),
            )

    def first(self):
        return execute(self.__proxy, self.__css)

    def all(self):
        return execute(self.__proxy, self.__css, list_result=True)


class QueryProcessor(object):

    def __init__(self, proxy):
        self.__proxy = proxy

    def __getattr__(self, item):
        return make_result(self.__proxy, item)

    def __call__(self, proxy_or_tag, **selector):
        if isinstance(proxy_or_tag, pyv.basestring):
            return self.from_object(
                QueryObject(proxy_or_tag, **selector),
            )

        return self.__class__(proxy_or_tag)

    @property
    def proxy(self):
        return self.__proxy

    @property
    def driver(self):
        return self.__proxy.driver

    @property
    def contains(self):
        return Contains

    def from_object(self, obj):
        if not isinstance(obj, QueryObject):
            raise TypeError('"{}" is not QueryObject instance'.format(type(obj)))

        return make_result(self.__proxy, obj.tag)(**obj.selector)


class Query(object):
    """
    For usability only.

    q = query('div', _class=query.contains('name'))
    result = q(browser)
    result.first()
    """

    @property
    def contains(self):
        return Contains

    def __call__(self, tag, **selector):
        return QueryObject(tag, **selector)


query = Query()
