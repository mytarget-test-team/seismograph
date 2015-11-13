# -*- coding: utf-8 -*-

from six import with_metaclass

from ...utils import pyv
from .query import QueryObject


def page_object_factory(page_element):
    def wrapper(self):
        if page_element.obj_class:
            result = page_element.get_instance(self.area)
        else:
            we = None

            for query_object in page_element.query_set[:-1]:
                if we:
                    we = we.query.from_object(
                        query_object,
                    ).first()
                else:
                    we = self.query.from_object(
                        query_object,
                    ).first()

            if we:
                result = we.query.from_object(page_element.query_set[-1:][0])
            else:
                result = self.query.from_object(page_element.query_set[-1:][0])

            if page_element.wait_timeout:
                result.wait(
                    page_element.wait_timeout,
                )

            if page_element.is_list:
                result = result.all()
            elif page_element.index:
                result = result.get(
                    page_element.index,
                )
            else:
                result = result.first()

        if page_element.proxy:
            if pyv.is_class_type(page_element.proxy):
                return page_element.proxy(result)
            return lambda: page_element.proxy(result)
        return result

    return property(wrapper)


class PageObjectProxy(object):

    def __init__(self, proxy):
        self.__wrapped = proxy

    def __getattr__(self, item):
        return getattr(self.__wrapped, item)

    def __repr__(self):
        return repr(self.__wrapped)

    @property
    def _wrapped(self):
        return self.__wrapped

    @property
    def driver(self):
        return self.__wrapped.driver


class PageObject(object):

    def __init__(self, *args, **options):
        assert bool(args), 'Element can not be created without args'

        self.__query_set = None
        self.__obj_class = None
        self.__obj_instance = None

        if pyv.is_class_type(args[0]):
            self.__obj_class = args[0]
        if isinstance(args[0], PageObject):
            self.__query_set = args[0].query_set + args[1:]
        else:
            self.__query_set = args

        self.__index = options.get('index', None)
        self.__proxy = options.get('proxy', None)
        self.__is_list = options.get('is_list', False)
        self.__wait_timeout = options.get('wait_timeout', None)

    def __call__(self, *args, **kwargs):
        # for IDE only
        raise TypeError(
            '"{}" object is not callable'.format(self.__class__.__name__),
        )

    def __getattr__(self, item):
        # for IDE only
        raise AttributeError(item)

    @property
    def obj_class(self):
        return self.__obj_class

    def get_instance(self, area):
        if self.__obj_instance is None:
            self.__obj_instance = self.__obj_class(area)
        return self.__obj_instance

    @property
    def query_set(self):
        return self.__query_set

    @property
    def index(self):
        return self.__index

    @property
    def is_list(self):
        return self.__is_list

    @property
    def proxy(self):
        return self.__proxy

    @proxy.setter
    def proxy(self, cls):
        assert issubclass(cls, PageObjectProxy), \
            '"{}" is not "PageObjectProxy" subclass'.format(
                cls.__name__,
        )
        self.__proxy = cls

    @property
    def wait_timeout(self):
        return self.__wait_timeout


class PageApi(object):

    def __init__(self, page):
        self.__page = page

    @property
    def page(self):
        return self.__page


class PageMeta(type):
    """
    Factory for creating page object class
    """

    def __new__(mcs, name, bases, dct):
        cls = type.__new__(mcs, name, bases, dct)

        cls_items = (
            (a, getattr(cls, a, None))
            for a in dir(cls)
            if not a.startswith('_')
        )

        for atr, value in cls_items:
            if isinstance(value, PageObject):
                setattr(cls, atr, page_object_factory(value))

        return cls


class Page(with_metaclass(PageMeta, object)):

    __wrapper__ = None
    __api_class__ = PageApi

    def __init__(self, proxy):
        self.__proxy = proxy
        self.__api = self.__api_class__(self)

    def __getattr__(self, item):
        return getattr(self.area, item)

    @property
    def api(self):
        return self.__api

    @property
    def area(self):
        if self.__wrapper__:
            if not isinstance(self.__wrapper__, QueryObject):
                raise TypeError(
                    '"__wrapper__" can be instance of QueryObject only',
                )
            return self.__proxy.query.from_object(
                self.__wrapper__,
            ).first()

        return self.__proxy

    @property
    def driver(self):
        return self.__proxy.driver

    @property
    def query(self):
        return self.area.query

    def relate_to(self, proxy):
        self.__proxy = proxy

    def refresh(self):
        self.__proxy.driver.refresh()
