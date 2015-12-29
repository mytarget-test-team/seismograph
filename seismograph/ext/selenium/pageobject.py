# -*- coding: utf-8 -*-

from six import with_metaclass

from ...utils import pyv
from .query import QueryObject


def query_set(page_object):
    return page_object.__query_set__()


def key(page_object):
    return page_object.__key__()


class PageObjectProxy(object):

    def __init__(self, proxy):
        self.__wrapped = proxy

    def __dir__(self):
        return list(set((dir(self._wrapped) + dir(self.__class__))))

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

    @property
    def config(self):
        return self.__wrapped.config


class PageObject(object):

    def __init__(self, *args, **options):
        assert bool(args), 'Element can not be created without arguments'

        self.__query_set = []
        self.__obj_class = None

        for a in args:
            if pyv.is_class_type(a):
                self.__obj_class = a
                break
            elif isinstance(a, PageObject):
                self.__query_set.extend(query_set(a))
            elif isinstance(a, QueryObject):
                self.__query_set.append(a)
            else:
                raise ValueError('Incorrect page object argument')

        self.__key = options.get('key', None)
        self.__index = options.get('index', None)
        self.__proxy = options.get('proxy', None)
        self.__action = options.get('action', None)
        self.__cached = options.get('cached', False)
        self.__handler = options.get('handler', None)
        self.__is_list = options.get('is_list', False)
        self.__wait_timeout = options.get('wait_timeout', None)

    def __getattr__(self, item):
        # for IDE only
        raise AttributeError(item)

    def __make_object__(self, page):
        if self.__cached and id(self) in page.cache:
            result = page.cache[id(self)]
        else:
            if self.__obj_class:
                result = self.__obj_class(page.area)
            else:
                we = None

                for query_object in self.__query_set[:-1]:
                    if we:
                        we = query_object(we).first()
                    else:
                        we = query_object(page.area).first()

                query_object = self.__query_set[-1:][0]

                if we:
                    query_result = query_object(we)
                else:
                    query_result = query_object(page.area)

                if self.__wait_timeout:
                    query_result.wait(
                        self.__wait_timeout,
                    )

                if self.__is_list:
                    result = query_result.all()
                elif self.__index:
                    result = query_result.get(
                        self.__index,
                    )
                else:
                    result = query_result.first()

        if self.__cached:
            page.cache[id(self)] = result

        return result

    def __get__(self, instance, owner):
        if instance is None:
            return self

        obj = self.__make_object__(instance)

        if self.__handler:
            return self.__handler(obj)

        if self.__action:
            return lambda *a, **k: self.__action(obj, *a, **k)

        if self.__proxy:
            return self.__proxy(obj)

        return obj

    def __set__(self, instance, value):
        raise TypeError('\'PageObject\' is not settable')

    def __key__(self):
        return self.__key

    def __query_set__(self):
        return self.__query_set


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

        setattr(cls, '__dct__', {})

        page_objects = (
            (a, getattr(cls, a, None))
            for a in dir(cls)
            if not a.startswith('_')
            and
            isinstance(getattr(cls, a, None), PageObject)
        )

        for atr_name, page_object in page_objects:
            if key(page_object):
                cls.__dct__[key(page_object)] = atr_name

        return cls


class Page(with_metaclass(PageMeta, object)):

    __wrapper__ = None
    __url_path__ = None
    __api_class__ = PageApi

    def __init__(self, proxy=None):
        self.__cache = {}
        self.__proxy = proxy
        self.__api = self.__api_class__(self)

    def __getitem__(self, item):
        try:
            return getattr(self, self.__class__.__dct__[item])
        except (KeyError, AttributeError):
            raise KeyError(item)

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
            return self.__wrapper__(self.__proxy).first()

        return self.__proxy

    @property
    def driver(self):
        return self.__proxy.driver

    @property
    def cache(self):
        return self.__cache

    def show(self, **kwargs):
        if self.__url_path__:
            self.driver.router.go_to(
                self.__url_path__.format(**kwargs),
            )
        else:
            raise RuntimeError(
                'You should to set "__url_path__" attribute value for usage "show" method',
            )

    def bind_to(self, proxy):
        self.__proxy = proxy

    def refresh(self):
        self.__cache.clear()
        self.__proxy.driver.refresh()


PageItem = Page


class TableProxy(PageObjectProxy):

    def apply_row_class(self, cls):
        for row in self._wrapped:
            index = self._wrapped.index(row)
            self._wrapped[index] = cls(row)

    def get_row(self, **kwargs):
        return self._wrapped.get_by(**kwargs)


class PageT(PageObject):

    def __init__(self, *args, **kwargs):
        self.__row_class = kwargs.pop('row_class', None)

        kwargs.update(is_list=True)
        kwargs.update(proxy=TableProxy)

        super(PageT, self).__init__(*args, **kwargs)

    def __make_object__(self, page):
        result = super(PageT, self).__make_object__(page)
        if self.__row_class:
            result.apply_row_class(self.__row_class)
        return result


class PageTable(PageItem):

    __row_class__ = None

    rows = None

    def get_rows(self):
        rows = self.rows

        if rows is None:
            raise NotImplementedError(
                'Property "rows" does not implemented in "{}"'.format(
                    self.__class__.__name__,
                ),
            )

        if self.__row_class__:
            for row in rows:
                index = rows.index(row)
                rows[index] = self.__row_class__(row)

        return rows

    def get_row(self, **kwargs):
        rows = self.get_rows()
        return rows.get_by(**kwargs)
