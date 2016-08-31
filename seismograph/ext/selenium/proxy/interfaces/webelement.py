# -*- coding: utf-8 -*-

from warnings import warn
from functools import wraps

from selenium.common.exceptions import StaleElementReferenceException

from .....utils import pyv
from .base import BaseInterface


def allow_ignore_stale(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.config.IGNORE_STALE_ELEMENT:
            try:
                return f(self, *args, **kwargs)
            except StaleElementReferenceException as error:
                warn(
                    'StaleElementReferenceException: {}'.format(
                        pyv.get_exc_message(error)
                    ),
                    RuntimeWarning,
                )
                return
        return f(self, *args, **kwargs)
    return wrapper


class WebElementInterface(BaseInterface):

    def __hash__(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('__hash__')(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('__eq__')(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('__ne__')(*args, **kwargs)

    @property
    def tag_name(self):
        return self.__getattr_from_webdriver_or_webelement__('tag_name')

    @property
    def text(self):
        return self.__getattr_from_webdriver_or_webelement__('text')

    @property
    def location_once_scrolled_into_view(self):
        return self.__getattr_from_webdriver_or_webelement__('location_once_scrolled_into_view')

    @property
    def size(self):
        return self.__getattr_from_webdriver_or_webelement__('size')

    @property
    def location(self):
        return self.__getattr_from_webdriver_or_webelement__('location')

    @property
    def rect(self):
        return self.__getattr_from_webdriver_or_webelement__('rect')

    @property
    def screenshot_as_base64(self):
        return self.__getattr_from_webdriver_or_webelement__('screenshot_as_base64')

    @property
    def screenshot_as_png(self):
        return self.__getattr_from_webdriver_or_webelement__('screenshot_as_png')

    @property
    def parent(self):
        return self.__getattr_from_webdriver_or_webelement__('parent')

    @property
    def id(self):
        return self.__getattr_from_webdriver_or_webelement__('id')

    def _execute(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('_execute')(*args, **kwargs)

    def _upload(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('_upload')(*args, **kwargs)

    @allow_ignore_stale
    def click(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('click')(*args, **kwargs)

    @allow_ignore_stale
    def submit(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('submit')(*args, **kwargs)

    @allow_ignore_stale
    def clear(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('clear')(*args, **kwargs)

    def get_attribute(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_attribute')(*args, **kwargs)

    def is_selected(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('is_selected')(*args, **kwargs)

    def is_enabled(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('is_enabled')(*args, **kwargs)

    def find_element_by_id(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_id')(*args, **kwargs)

    def find_elements_by_id(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_id')(*args, **kwargs)

    def find_element_by_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_name')(*args, **kwargs)

    def find_elements_by_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_name')(*args, **kwargs)

    def find_element_by_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_link_text')(*args, **kwargs)

    def find_elements_by_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_link_text')(*args, **kwargs)

    def find_element_by_partial_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_partial_link_text')(*args, **kwargs)

    def find_elements_by_partial_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_partial_link_text')(*args, **kwargs)

    def find_element_by_tag_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_tag_name')(*args, **kwargs)

    def find_elements_by_tag_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_tag_name')(*args, **kwargs)

    def find_element_by_xpath(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_xpath')(*args, **kwargs)

    def find_elements_by_xpath(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_xpath')(*args, **kwargs)

    def find_element_by_class_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_class_name')(*args, **kwargs)

    def find_elements_by_class_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_class_name')(*args, **kwargs)

    def find_element_by_css_selector(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_css_selector')(*args, **kwargs)

    def find_elements_by_css_selector(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_css_selector')(*args, **kwargs)

    @allow_ignore_stale
    def send_keys(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('send_keys')(*args, **kwargs)

    @allow_ignore_stale
    def set(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('send_keys')(*args, **kwargs)

    def is_displayed(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('is_displayed')(*args, **kwargs)

    def value_of_css_property(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('value_of_css_property')(*args, **kwargs)

    def screenshot(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('screenshot')(*args, **kwargs)

    def find_element(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element')(*args, **kwargs)

    def find_elements(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements')(*args, **kwargs)
