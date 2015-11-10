# -*- coding: utf-8 -*-

from __future__ import absolute_import

from types import MethodType
from contextlib import contextmanager

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from .router import Router
from .tools import polling
from .tools import make_object
from .tools import ActionChains
from .query import QueryProcessor


METHOD_ALIASES = {
    'go_to': 'get',
    'set': 'send_keys',
}


def factory_method(f, driver, config, allow_polling=True, reason_storage=None):
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)

        if isinstance(result, WebElement):
            return WebElementProxy(
                result,
                config=config,
                driver=driver,
                allow_polling=allow_polling,
                reason_storage=reason_storage,
            )

        if isinstance(result, list):
            we_list = WebElementList()

            for obj in result:
                if isinstance(obj, WebElement):
                    we_list.append(
                        WebElementProxy(
                            obj,
                            config=config,
                            allow_polling=allow_polling,
                            reason_storage=reason_storage,
                        ),
                    )
                else:
                    return result

            return we_list
        return result
    return wrapper


class WebElementList(list):

    def get_by(self, **kwargs):
        for we in self:
            if all(getattr(we.attr, k) == v for k, v in kwargs.items()):
                return we
        else:
            raise NoSuchElementException(
                u'by filters "{}" of list {}'.format(
                    u', '.join(
                        u'{}={}'.format(k, v) for k, v in kwargs.items()
                    ),
                    repr(self),
                ),
            )

    def filter(self, **kwargs):
        result = []

        for we in self:
            if all(getattr(we.attr, k) == v for k, v in kwargs.items()):
                result.append(we)

        return result


class BaseProxy(object):

    def __init__(self, wrapped, config=None, driver=None, reason_storage=None, allow_polling=True):
        self.__dict__['__driver__'] = driver
        self.__dict__['__config__'] = config
        self.__dict__['__wrapped__'] = wrapped
        self.__dict__['__query__'] = QueryProcessor(self)
        self.__dict__['__allow_polling__'] = allow_polling
        self.__dict__['__reason_storage__'] = reason_storage or dict()

        assert self.__class__ != BaseProxy, 'This is base class only. Can not be instanced.'

    def __repr__(self):
        return repr(self._wrapped)

    def __getattr__(self, item):
        attr = getattr(
            self._wrapped, METHOD_ALIASES.get(item, item), None,
        )

        if attr is None:
            attr = getattr(self.query, item)

        if callable(attr) and type(attr) == MethodType:
            if self.allow_polling:
                return polling(
                    callback=factory_method(
                        attr,
                        self.driver,
                        self.config,
                        allow_polling=self.allow_polling,
                        reason_storage=self.reason_storage,
                    ),
                    timeout=self.config.POLLING_TIMEOUT,
                )

            return factory_method(
                attr,
                self.driver,
                self.config,
                allow_polling=self.allow_polling,
                reason_storage=self.reason_storage,
            )

        return attr

    @property
    def _wrapped(self):
        return self.__dict__['__wrapped__']

    @property
    def config(self):
        return self.__dict__['__config__']

    @property
    def query(self):
        return self.__dict__['__query__']

    @property
    def driver(self):
        return self.__dict__['__driver__']

    @property
    def allow_polling(self):
        return (
            bool(self.config.POLLING_TIMEOUT) and self.__dict__['__allow_polling__']
        )

    @property
    def reason_storage(self):
        return self.__dict__['__reason_storage__']

    @property
    def text(self):
        def get_text():
            if isinstance(self._wrapped, WebElement):
                return self._wrapped.text
            return self._wrapped.find_element_by_tag_name('body').text

        if self.allow_polling:
            func = polling(
                get_text,
                timeout=self.config.POLLING_TIMEOUT,
            )
            return func()

        return get_text()

    @contextmanager
    def disable_polling(self):
        try:
            self.__dict__['__allow_polling__'] = False
            yield
        finally:
            self.__dict__['__allow_polling__'] = True


class WebElementProxy(BaseProxy):

    def __init__(self, *args, **kwargs):
        super(WebElementProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebElement), 'This is proxy to WebElement only'

    @property
    def attr(self):
        return make_object(self, allow_raise=False)


class WebDriverProxy(BaseProxy):

    def __init__(self, *args, **kwargs):
        super(WebDriverProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebDriver), 'This is proxy to WebDriver only'

        self.__dict__['__router__'] = Router(self)
        self.__dict__['__action_chains__'] = ActionChains(self)

    @property
    def driver(self):
        return self

    @property
    def router(self):
        return self.__dict__['__router__']

    @property
    def action_chains(self):
        return self.__dict__['__action_chains__']

    @property
    def current_url(self):
        if self.allow_polling:
            func = polling(
                lambda: self._wrapped.current_url,
                timeout=self.config.POLLING_TIMEOUT,
            )
            return func()

        return self._wrapped.current_url
