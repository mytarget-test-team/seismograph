# -*- coding: utf-8 -*-

from functools import wraps
from types import MethodType
from collections import OrderedDict
from contextlib import contextmanager

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from . import polling
from .router import Router
from .query import QueryProcessor
from ...utils.common import waiting_for
from .utils import change_name_from_python_to_html


METHOD_ALIASES = {
    'go_to': 'get',
    'set': 'send_keys',
}


def _check_equal(we, attr, value):
    if attr == 'text':
        return we.text == value

    return getattr(we.attr, attr) == value


def factory_method(f, driver, config, allow_polling=True, reason_storage=None):
    @wraps(f)
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

        if isinstance(result, (list, tuple)):
            we_list = WebElementListProxy(
                driver,
                config,
                reason_storage=reason_storage,
            )

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


class WebElementListProxy(list):

    def __init__(self, driver, config, reason_storage=None):
        super(WebElementListProxy, self).__init__()

        self.__driver = driver
        self.__config = config
        self.__reason_storage = reason_storage or OrderedDict()

    @property
    def driver(self):
        return self.__driver

    @property
    def config(self):
        return self.__config

    @property
    def query(self):
        return self.__driver.query

    @property
    def reason_storage(self):
        return self.__reason_storage

    def get_by(self, **kwargs):
        try:
            return next(
                we for we in self
                if all(_check_equal(we, k, v) for k, v in kwargs.items())
            )
        except StopIteration:
            pass

    def filter(self, **kwargs):
        for we in self:
            if all(_check_equal(we, k, v) for k, v in kwargs.items()):
                yield we


class BaseProxy(object):

    def __init__(self, wrapped, config=None, driver=None, reason_storage=None, allow_polling=True):
        self.__driver = driver
        self.__config = config
        self.__wrapped = wrapped
        self.__query = QueryProcessor(self)
        self.__allow_polling = allow_polling
        self.__reason_storage = reason_storage or OrderedDict()

        assert self.__class__ != BaseProxy, 'This is base class only. Can not be instanced.'

    def __repr__(self):
        return repr(self._wrapped)

    def __getattr__(self, item):
        attr = getattr(
            self._wrapped, METHOD_ALIASES.get(item, item), None,
        )

        if attr is None:
            return getattr(self.query, item)

        if callable(attr) and type(attr) == MethodType:
            if self.allow_polling:
                return polling.do(
                    callback=factory_method(
                        attr,
                        self.driver,
                        self.config,
                        allow_polling=self.allow_polling,
                        reason_storage=self.reason_storage,
                    ),
                    delay=self.config.POLLING_DELAY,
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
        return self.__wrapped

    @property
    def config(self):
        return self.__config

    @property
    def query(self):
        return self.__query

    @property
    def driver(self):
        return self.__driver

    @property
    def allow_polling(self):
        return (
            bool(self.config.POLLING_TIMEOUT) and self.__allow_polling
        )

    @property
    def reason_storage(self):
        return self.__reason_storage

    @property
    def text(self):
        def get_text():
            if isinstance(self._wrapped, WebElement):
                return self._wrapped.text
            return self._wrapped.find_element_by_tag_name('body').text

        if self.allow_polling:
            func = polling.do(
                get_text,
                delay=self.config.POLLING_DELAY,
                timeout=self.config.POLLING_TIMEOUT,
            )
            return func()

        return get_text()

    @contextmanager
    def polling(self, func=None, exc_cls=None, message=None, timeout=None, args=None, kwargs=None):
        to_restore = self.__allow_polling
        self.__allow_polling = True

        if func:
            waiting_for(
                func,
                args=args,
                kwargs=kwargs,
                exc_cls=exc_cls,
                message=message,
                delay=self.config.POLLING_DELAY,
                timeout=timeout or self.config.POLLING_TIMEOUT or 0.5,
            )

        try:
            yield
        finally:
            self.__allow_polling = to_restore

    @contextmanager
    def disable_polling(self):
        try:
            self.__allow_polling = False
            yield
        finally:
            self.__allow_polling = True


class WebElementProxy(BaseProxy):

    def __init__(self, *args, **kwargs):
        super(WebElementProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebElement), 'This is proxy to WebElement only'

    @property
    def css(self):
        return WebElementCssToObject(self)

    @property
    def attr(self):
        return WebElementToObject(self, allow_raise=False)


class WebDriverProxy(BaseProxy):

    def __init__(self, *args, **kwargs):
        super(WebDriverProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebDriver), 'This is proxy to WebDriver only'

        self.__router = Router(self)
        self.__action_chains = ActionChainsProxy(self)

    @property
    def driver(self):
        return self

    @property
    def router(self):
        return self.__router

    @property
    def action_chains(self):
        return self.__action_chains

    @property
    def current_url(self):
        if self.allow_polling:
            func = polling.do(
                lambda: self._wrapped.current_url,
                delay=self.config.POLLING_DELAY,
                timeout=self.config.POLLING_TIMEOUT,
            )
            return func()

        return self._wrapped.current_url


class ActionChainsProxy(object):

    def __init__(self, proxy):
        self.__action_chains = ActionChains(proxy.driver)

    def __call__(self, proxy):
        return self.__class__(proxy.driver)

    def __getattr__(self, item):
        return getattr(self.__action_chains, item)

    def __repr__(self):
        return repr(self.__action_chains)

    def reset(self):
        self.__action_chains._actions = []

    def perform(self, reset=True):
        self.__action_chains.perform()

        if reset:
            self.reset()


class WebElementToObject(object):

    def __init__(self, proxy, allow_raise=True):
        self.__dict__['__proxy__'] = proxy
        self.__dict__['__allow_raise__'] = allow_raise

    def __getattr__(self, item):
        atr = self.__dict__['__proxy__'].get_attribute(
            change_name_from_python_to_html(item),
        )

        if atr:
            return atr

        if self.__dict__['__allow_raise__']:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        self.__dict__['__proxy__'].parent.execute_script(
            'arguments[0].setAttribute(arguments[1], arguments[2]);',
            self.__dict__['__proxy__'],
            change_name_from_python_to_html(key),
            value
        )


class WebElementCssToObject(object):

    def __init__(self, proxy):
        self.__dict__['__proxy__'] = proxy

    def __getattr__(self, item):
        return self.__dict__['__proxy__'].value_of_css_property(
            change_name_from_python_to_html(item),
        )

    def __setattr__(self, key, value):
        self.__dict__['__proxy__'].parent.execute_script(
            'arguments[0].style[arguments[1]] = arguments[2];',
            self.__dict__['__proxy__'],
            change_name_from_python_to_html(key),
            value
        )
