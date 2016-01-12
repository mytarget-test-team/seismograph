# -*- coding: utf-8 -*-

import time
from functools import wraps
from types import MethodType
from collections import OrderedDict
from contextlib import contextmanager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.action_chains import ActionChains

from . import polling
from ...utils import pyv
from .router import Router
from .query import make_result
from ...utils.common import waiting_for
from .utils import is_ready_state_complete
from .utils import change_name_from_python_to_html


METHOD_ALIASES = {
    'go_to': 'get',
    'set': 'send_keys',
}


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
                            driver=driver,
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
    def reason_storage(self):
        return self.__reason_storage

    def get_by(self, **kwargs):
        try:
            return next(self.filter(**kwargs))
        except StopIteration:
            pass

    def filter(self, **kwargs):
        def check_equal(we, attr, value):
            attr_value = getattr(we, attr, None)
            if callable(attr_value) or attr_value is None:
                attr_value = getattr(we.attr, attr)
            return attr_value == value

        for we in self:
            if all(check_equal(we, k, v) for k, v in kwargs.items()):
                yield we


class BaseProxy(object):

    def __init__(self, wrapped, config=None, driver=None, reason_storage=None, allow_polling=True):
        self.__driver = driver
        self.__config = config
        self.__wrapped = wrapped
        self.__allow_polling = allow_polling
        self.__reason_storage = reason_storage or OrderedDict()

        assert self.__class__ != BaseProxy, 'This is base class only. Can not be instanced.'

    def __len__(self):
        if isinstance(self._wrapped, WebElement):
            area = self
        else:
            area = self.body().first()

        try:
            return len(area.attr.innerHTML)
        except (TypeError, WebDriverException):
            return 0

    def __nonzero__(self):
        return True

    def __bool__(self):  # please python 3
        return self.__nonzero__()

    def __dir__(self):
        return list((dir(self._wrapped) + dir(self.__class__)))

    def __repr__(self):
        return repr(self._wrapped)

    def __getattr__(self, item):
        attr = getattr(
            self._wrapped, METHOD_ALIASES.get(item, item), None,
        )

        if attr is None:
            return make_result(self, item)

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

    @property
    def is_web_element(self):
        raise NotImplementedError(
            'Property "is_web_element" does not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    @contextmanager
    def polling(self,
                func=None,
                exc_cls=None,
                message=None,
                timeout=None,
                delay=None,
                args=None,
                kwargs=None):
        to_restore = self.__allow_polling
        self.__allow_polling = True

        try:
            if func:
                yield waiting_for(
                    func,
                    args=args,
                    kwargs=kwargs,
                    exc_cls=exc_cls,
                    message=message,
                    delay=delay or self.config.POLLING_DELAY,
                    timeout=timeout or self.config.POLLING_TIMEOUT,
                )
            else:
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

    @contextmanager
    def confirm_action(self, callback, timeout=None, delay=None):
        delay = delay or self.config.POLLING_DELAY
        timeout = timeout or self.config.POLLING_TIMEOUT

        try:
            yield
        finally:
            waiting_for(
                callback,
                delay=delay,
                timeout=timeout,
                exc_cls=polling.PollingTimeoutExceeded,
                message='Action has not been confirmed for "{}" sec.'.format(timeout),
            )

    def wait_ready(self, tries=15, delay=0.01):
        waiting_for(
            is_ready_state_complete,
            args=(self.driver, ),
            delay=self.config.POLLING_DELAY,
            timeout=self.config.POLLING_TIMEOUT,
            message='Timeout waiting for load page',
        )

        def is_update():
            length = [
                (len(self), time.sleep(delay), len(self))
                for _ in pyv.xrange(tries)
            ]
            statuses = [d[0] < d[2] for d in length]
            return True in statuses or length[0][0] != length[-1:][0][2]

        while is_update():
            time.sleep(delay)


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

    @property
    def is_web_element(self):
        return True

    def double_click(self):
        with self.driver.action_chains as action:
            action.double_click(self)

    def context_click(self):
        with self.driver.action_chains as action:
            action.context_click(self)


class WebDriverProxy(BaseProxy):

    keys = Keys

    def __init__(self, *args, **kwargs):
        super(WebDriverProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebDriver), 'This is proxy to WebDriver only'

        self.__router = Router(self)
        self.__alert = AlertProxy(self)
        self.__action_chains = ActionProxy(self, ActionChains)
        self.__touch_actions = ActionProxy(self, TouchActions)

    @property
    def driver(self):
        return self

    @property
    def router(self):
        return self.__router

    @property
    def alert(self):
        return self.__alert

    @property
    def action_chains(self):
        return self.__action_chains

    @property
    def touch_actions(self):
        return self.__touch_actions

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

    @property
    def current_path(self):
        if not self.config.PROJECT_URL:
            raise RuntimeError(
                'Can not calculate current path. PROJECT_URL is not set.',
            )
        return self.current_url.replace(self.config.PROJECT_URL, '')

    @property
    def is_web_element(self):
        return False


class AlertProxy(object):

    def __init__(self, proxy):
        self.__alert = Alert(proxy.driver)

    def __dir__(self):
        return dir(self.__alert)

    def __call__(self, proxy):
        return self.__class__(proxy.driver)

    def __getattr__(self, item):
        return getattr(self.__alert, item)

    def __repr__(self):
        return repr(self.__alert)


class ActionProxy(object):

    def __init__(self, proxy, cls):
        self.__action = cls(proxy.driver)

    def __call__(self, proxy=None):
        return self.__class__(
            proxy.driver if proxy else self.__action._driver,
            cls=self.__action.__class__,
        )

    def __dir__(self):
        return list(set(dir(self.__action) + dir(self.__class__)))

    def __getattr__(self, item):
        return getattr(self.__action, item)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        try:
            self.perform()
        finally:
            self.reset()

    def __repr__(self):
        return repr(self.__action)

    @property
    def driver(self):
        return self.__action._driver

    def reset(self):
        self.__action._actions = []


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
            self.__dict__['__proxy__']._wrapped,
            change_name_from_python_to_html(key),
            value,
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
            self.__dict__['__proxy__']._wrapped,
            change_name_from_python_to_html(key),
            value,
        )
