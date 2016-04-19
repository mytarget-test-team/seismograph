# -*- coding: utf-8 -*-

import time
from functools import wraps
from types import MethodType
from collections import OrderedDict
from contextlib import contextmanager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement

from . import tools
from . import actions
from .. import polling
from ....utils import pyv
from ..router import Router
from ..query import make_result
from ....utils.common import waiting_for
from .interfaces import WebDriverInterface
from .interfaces import WebElementInterface
from ..utils import is_ready_state_complete
from .interfaces import HTML_TAGS_ALLOWED_AS_METHOD


def factory_method(f, browser, config, allow_polling=True, reason_storage=None):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)

        if isinstance(result, WebElement):
            return WebElementProxy(
                result,
                config=config,
                browser=browser,
                allow_polling=allow_polling,
                reason_storage=reason_storage,
            )

        if isinstance(result, (list, tuple)):
            we_list = WebElementList(
                browser,
                config,
                reason_storage=reason_storage,
            )

            for obj in result:
                if isinstance(obj, WebElement):
                    we_list.append(
                        WebElementProxy(
                            obj,
                            browser=browser,
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

    def __init__(self, browser, config, reason_storage=None):
        super(WebElementList, self).__init__()

        self.__browser = browser
        self.__config = config
        self.__reason_storage = reason_storage or OrderedDict()

    @property
    def browser(self):
        return self.__browser

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

    def __init__(self, wrapped, config=None, browser=None, reason_storage=None, allow_polling=True):
        self.__browser = browser
        self.__config = config
        self.__wrapped = wrapped
        self._allow_polling = allow_polling
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
        if item in HTML_TAGS_ALLOWED_AS_METHOD:
            return make_result(self, item)

        raise AttributeError(
            '"{}" has not attribute "{}"'.format(
                self.__class__.__name__, item,
            ),
        )

    def __getattr_from_webdriver_or_webelement__(self, item):
        attr = getattr(self._wrapped, item)

        if callable(attr) and type(attr) == MethodType:
            if self.allow_polling:
                return polling.do(
                    factory_method(
                        attr,
                        self.browser,
                        self.config,
                        allow_polling=self.allow_polling,
                        reason_storage=self.reason_storage,
                    ),
                    delay=self.config.POLLING_DELAY,
                    timeout=self.config.POLLING_TIMEOUT,
                )

            return factory_method(
                attr,
                self.browser,
                self.config,
                allow_polling=self.allow_polling,
                reason_storage=self.reason_storage,
            )

        return attr

    def __setattr_to_webdriver_or_webelement__(self, item, value):
        setattr(self._wrapped, item, value)

    @property
    def _wrapped(self):
        return self.__wrapped

    @property
    def config(self):
        return self.__config

    @property
    def browser(self):
        return self.__browser

    @property
    def allow_polling(self):
        return (
            bool(self.config.POLLING_TIMEOUT) and self._allow_polling
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
    def do_polling(self,
                   callback,
                   exceptions=None,
                   timeout=None,
                   delay=None):
        return polling.do(
            callback,
            exceptions=exceptions or polling.POLLING_EXCEPTIONS,
            delay=delay or self.config.POLLING_DELAY,
            timeout=timeout or self.config.POLLING_TIMEOUT,
        )

    def waiting_for(self,
                    callback,
                    timeout=None,
                    exc_cls=None,
                    message=None,
                    delay=None,
                    args=None,
                    kwargs=None):
        delay = delay or self.config.POLLING_DELAY
        timeout = timeout or self.config.POLLING_TIMEOUT
        exc_cls = exc_cls or polling.PollingTimeoutExceeded
        message = message or 'Wait timeout "{}" has been exceeded'.format(timeout)

        return waiting_for(
            callback,
            args=args,
            kwargs=kwargs,
            delay=delay,
            timeout=timeout,
            exc_cls=exc_cls,
            message=message,
        )

    @contextmanager
    def disable_polling(self):
        try:
            self._allow_polling = False
            yield
        finally:
            self._allow_polling = True

    def wait_ready(self, tries=15, delay=0.01):
        waiting_for(
            is_ready_state_complete,
            args=(self.browser, ),
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


class WebElementProxy(BaseProxy, WebElementInterface):

    def __init__(self, *args, **kwargs):
        super(WebElementProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebElement), 'This is proxy to WebElement only'

    @property
    def css(self):
        return tools.WebElementCssToObject(self)

    @property
    def attr(self):
        return tools.WebElementToObject(self, allow_raise=False)

    @property
    def is_web_element(self):
        return True

    def double_click(self):
        with self.browser.action_chains as action:
            action.double_click(self)
            action.perform()

    def context_click(self):
        with self.browser.action_chains as action:
            action.context_click(self)
            action.perform()


class WebDriverProxy(BaseProxy, WebDriverInterface):

    keys = Keys

    def __init__(self, *args, **kwargs):
        super(WebDriverProxy, self).__init__(*args, **kwargs)

        assert isinstance(self._wrapped, WebDriver), 'This is proxy to WebDriver only'

        self.__router = Router(self)
        self.__alert = actions.Alert(self)
        self.__action_chains = actions.ActionChains(self)
        self.__touch_actions = actions.TouchActions(self)

    @property
    def browser(self):
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
