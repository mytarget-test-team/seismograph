# -*- coding: utf-8 -*-

import logging

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from ...utils.common import waiting_for
from .exceptions import PollingTimeoutExceeded
from .utils import change_name_from_python_to_html


logger = logging.getLogger(__name__)


TAG_ALIASES = {
    'any': '*',
}

ATTRIBUTE_ALIASES = {
    '_id': 'id',
    '_class': 'class',
    '_type': 'type',
    'id_': 'id',
    'class_': 'class',
    'type_': 'type',
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
        css = [tag_by_alias(tag)]

        def get_format(value):
            if isinstance(value, Contains):
                return u'[{}*="{}"]'
            return u'[{}="{}"]'

        css.extend(
            (
                get_format(val).format(attribute_by_alias(atr), val)
                for atr, val in selector.items()
            ),
        )

        return QueryResult(proxy, ''.join(css))

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
            wait_timeout = proxy.config.WAIT_TIMEOUT
            proxy.config.WAIT_TIMEOUT = 0
            try:
                method = get_execute_method(proxy, list_result)
                result = method(css)
            finally:
                proxy.config.WAIT_TIMEOUT = wait_timeout
        return result

    method = get_execute_method(proxy, list_result)
    return method(css)


class QueryResult(object):

    def __init__(self, proxy, css):
        self.__we = None

        self.__css = css
        self.__proxy = proxy

    def __repr__(self):
        return 'QueryResult({}): {}'.format(self.__css, repr(self.__proxy))

    def __getattr__(self, item):
        if not self.__we:
           self.first()
        return getattr(self.__we, item)

    def __css_string__(self):
        return self.__css

    @property
    def exist(self):
        """
        Check exist first element of query

        :rtype: bool
        """
        try:
            el = execute(self.__proxy, self.__css, disable_polling=True)

            if el:
                return True
            return False
        except WebDriverException:
            return False

    def wait(self, timeout=None, delay=None):
        """
        Wait for first element of query while timeout doesn't exceeded

        :param timeout: time for wait in seconds
        """
        return waiting_for(
            lambda: self.exist,
            exc_cls=PollingTimeoutExceeded,
            delay=delay or self.__proxy.config.POLLING_DELAY,
            timeout=timeout or self.__proxy.config.POLLING_TIMEOUT,
            message='Could not wait web element by css "{}"'.format(self.__css),
        )

    def get(self, index):
        """
        Get element of query by index

        :param index: index of element
        """
        try:
            self.__we = execute(self.__proxy, self.__css, list_result=True)[index]
            return self.__we
        except IndexError:
            raise NoSuchElementException(
                'Result does not have element by index "{}". Css query: "{}".'.format(
                    index, self.__css,
                ),
            )

    def first(self):
        """
        Get first element of query
        """
        self.__we = execute(self.__proxy, self.__css)
        return self.__we

    def all(self):
        """
        Get all elements of query
        """
        return execute(self.__proxy, self.__css, list_result=True)


class Query(object):
    """
    Make query data for execution.

    q = query(query.DIV, _class=query.contains('name'))
    result = q(browser)
    result.first()
    """

    A = 'a'
    B = 'b'
    P = 'p'
    U = 'u'
    UL = 'ul'
    LI = 'li'
    BR = 'br'
    EM = 'em'
    HR = 'hr'
    TR = 'tr'
    TD = 'td'
    TH = 'th'
    TT = 'tt'
    VAR = 'var'
    IMG = 'img'
    DIV = 'div'
    MAP = 'map'
    HEAD = 'head'
    FORM = 'form'
    BODY = 'body'
    AREA = 'area'
    CODE = 'code'
    BASE = 'base'
    SPAN = 'span'
    LINK = 'link'
    META = 'meta'
    SMALL = 'small'
    TABLE = 'table'
    INPUT = 'input'
    LABEL = 'label'
    FRAME = 'frame'
    EMBED = 'embed'
    BLINK = 'blink'
    IFRAME = 'iframe'
    CENTER = 'center'
    STRONG = 'strong'
    BUTTON = 'button'
    OBJECT = 'object'
    OPTION = 'option'
    SELECT = 'select'
    TEXTAREA = 'textarea'
    OPTGROUP = 'optgroup'
    FRAMESET = 'frameset'

    ANY = '*'

    contains = Contains

    @staticmethod
    def css_string(query_result):
        return query_result.__css_string__()

    def __call__(self, tag, **selector):
        return QueryObject(tag, **selector)


query = Query()
