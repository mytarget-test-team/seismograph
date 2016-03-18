# -*- coding: utf-8 -*-

from ..utils import change_name_from_python_to_html


class WebElementToObject(object):
    """
    Get a chance for work with attributes
    of HTML tag as attributes of the object
    """

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
    """
    Like WebElementToObject but work with css attributes
    """

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
