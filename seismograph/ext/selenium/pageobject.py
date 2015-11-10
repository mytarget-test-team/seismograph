# -*- coding: utf-8 -*-

from six import with_metaclass

from .query import QueryObject


def page_object_factory(page_element):
    def wrapper(self):
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

        if page_element.proxy_class:
            return page_element.proxy_class(result)
        return result

    return property(wrapper)


class PageObjectProxy(object):

    def __init__(self, obj):
        self.__obj = obj

    def __getattr__(self, item):
        return getattr(self.__obj, item)

    def __repr__(self):
        return repr(self.result)

    @property
    def obj(self):
        return self.__obj


class PageObject(object):

    def __init__(self, *query_set, **options):
        assert bool(query_set), 'Element can not be created without query set'

        if isinstance(query_set[0], PageObject):
            self.__query_set = query_set[0].query_set + query_set[1:]
        else:
            self.__query_set = query_set

        self.__index = options.get('index', None)
        self.__is_list = options.get('is_list', False)
        self.__proxy_class = options.get('proxy_class', None)
        self.__wait_timeout = options.get('wait_timeout', None)

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
    def proxy_class(self):
        return self.__proxy_class

    @proxy_class.setter
    def proxy_class(self, cls):
        assert issubclass(cls, PageObjectProxy), \
            '"{}" is not "PageObjectProxy" subclass'.format(
                cls.__name__,
        )
        self.__proxy_class = cls

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


class Forms(object):

    def __init__(self, **classes):
        self.__area = None
        self.__instances = {}

        self.__classes = classes

    def __getattr__(self, item):
        if not self.__area:
            raise RuntimeError('Need area for create instance')

        if item not in self.__instances:
            self.__instances[item] = self.__classes[item](self.__area)

        return self.__instances[item]

    def __call__(self, proxy):
        inst = self.__class__(**self.__classes)
        inst.change_area(proxy)
        return inst

    def add(self, name, cls):
        self.__classes[name] = cls

    def change_area(self, proxy):
        self.__area = proxy

    def refresh(self):
        self.__instances = {}


class Page(with_metaclass(PageMeta, object)):

    __wrapper__ = None
    __forms__ = Forms()
    __api_class__ = PageApi

    def __init__(self, proxy):
        self.__proxy = proxy
        self.__api = self.__api_class__(self)
        self.__forms = self.__forms__(self.area)

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

    @property
    def forms(self):
        return self.__forms

    def relate_to(self, proxy):
        self.__proxy = proxy
        self.__forms.change_area(self.area)

    def refresh(self, force=False):
        if force:
            self.__proxy.driver.refresh()
        self.__forms.refresh()
