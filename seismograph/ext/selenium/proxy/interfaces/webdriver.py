# -*- coding: utf-8 -*-

from .base import BaseInterface


class CommonWebDriverInterface(BaseInterface):
    """
    Common interface for all drivers
    """

    @property
    def mobile(self):
        return self.__getattr_from_webdriver_or_webelement__('mobile')

    @property
    def title(self):
        return self.__getattr_from_webdriver_or_webelement__('title')

    @property
    def name(self):
        return self.__getattr_from_webdriver_or_webelement__('name')

    @property
    def current_url(self):
        return self.__getattr_from_webdriver_or_webelement__('current_url')

    @property
    def page_source(self):
        return self.__getattr_from_webdriver_or_webelement__('page_source')

    @property
    def current_window_handle(self):
        return self.__getattr_from_webdriver_or_webelement__('current_window_handle')

    @property
    def window_handles(self):
        return self.__getattr_from_webdriver_or_webelement__('window_handles')

    @property
    def switch_to(self):
        return self.__getattr_from_webdriver_or_webelement__('switch_to')

    @property
    def desired_capabilities(self):
        return self.__getattr_from_webdriver_or_webelement__('desired_capabilities')

    @property
    def file_detector(self):
        return self.__getattr_from_webdriver_or_webelement__('file_detector')

    @file_detector.setter
    def file_detector(self, detector):
        self.__setattr_to_webdriver_or_webelement__('file_detector', detector)

    @property
    def orientation(self):
        return self.__getattr_from_webdriver_or_webelement__('orientation')

    @orientation.setter
    def orientation(self, value):
        self.__setattr_to_webdriver_or_webelement__('orientation', value)

    @property
    def application_cache(self):
        return self.__getattr_from_webdriver_or_webelement__('application_cache')

    @property
    def log_types(self):
        return self.__getattr_from_webdriver_or_webelement__('log_types')

    def start_client(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('start_client')(*args, **kwargs)

    def stop_client(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('stop_client')(*args, **kwargs)

    def start_session(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('start_session')(*args, **kwargs)

    def _wrap_value(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('_wrap_value')(*args, **kwargs)

    def create_web_element(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('create_web_element')(*args, **kwargs)

    def _unwrap_value(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('_unwrap_value')(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('execute')(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get')(*args, **kwargs)

    def go_to(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get')(*args, **kwargs)

    def find_element_by_id(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_id')(*args, **kwargs)

    def find_elements_by_id(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_id')(*args, **kwargs)

    def find_element_by_xpath(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_xpath')(*args, **kwargs)

    def find_elements_by_xpath(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_xpath')(*args, **kwargs)

    def find_element_by_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_link_text')(*args, **kwargs)

    def find_elements_by_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_link_text')(*args, **kwargs)

    def find_element_by_partial_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_partial_link_text')(*args, **kwargs)

    def find_elements_by_partial_link_text(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_partial_link_text')(*args, **kwargs)

    def find_element_by_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_name')(*args, **kwargs)

    def find_elements_by_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_name')(*args, **kwargs)

    def find_element_by_tag_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_tag_name')(*args, **kwargs)

    def find_elements_by_tag_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_tag_name')(*args, **kwargs)

    def find_element_by_class_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_class_name')(*args, **kwargs)

    def find_elements_by_class_name(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_class_name')(*args, **kwargs)

    def find_element_by_css_selector(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element_by_css_selector')(*args, **kwargs)

    def find_elements_by_css_selector(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements_by_css_selector')(*args, **kwargs)

    def execute_script(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('execute_script')(*args, **kwargs)

    def execute_async_script(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('execute_async_script')(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('close')(*args, **kwargs)

    def quit(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('quit')(*args, **kwargs)

    def maximize_window(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('maximize_window')(*args, **kwargs)

    def switch_to_active_element(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('switch_to_active_element')(*args, **kwargs)

    def switch_to_window(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('switch_to_window')(*args, **kwargs)

    def switch_to_frame(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('switch_to_frame')(*args, **kwargs)

    def switch_to_default_content(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('switch_to_default_content')(*args, **kwargs)

    def switch_to_alert(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('switch_to_alert')(*args, **kwargs)

    def back(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('back')(*args, **kwargs)

    def forward(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('forward')(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('refresh')(*args, **kwargs)

    def get_cookies(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_cookies')(*args, **kwargs)

    def get_cookie(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_cookie')(*args, **kwargs)

    def delete_cookie(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('delete_cookie')(*args, **kwargs)

    def delete_all_cookies(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('delete_all_cookies')(*args, **kwargs)

    def add_cookie(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('add_cookie')(*args, **kwargs)

    def implicitly_wait(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('implicitly_wait')(*args, **kwargs)

    def set_script_timeout(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('set_script_timeout')(*args, **kwargs)

    def set_page_load_timeout(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('set_page_load_timeout')(*args, **kwargs)

    def find_element(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_element')(*args, **kwargs)

    def find_elements(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('find_elements')(*args, **kwargs)

    def get_screenshot_as_file(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_screenshot_as_file')(*args, **kwargs)

    def save_screenshot(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('save_screenshot')(*args, **kwargs)

    def get_screenshot_as_png(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_screenshot_as_png')(*args, **kwargs)

    def get_screenshot_as_base64(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_screenshot_as_base64')(*args, **kwargs)

    def set_window_size(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('set_window_size')(*args, **kwargs)

    def get_window_size(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_window_size')(*args, **kwargs)

    def set_window_position(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('set_window_position')(*args, **kwargs)

    def get_window_position(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_window_position')(*args, **kwargs)

    def get_log(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('get_log')(*args, **kwargs)


class ChromeWebDriverInterface(BaseInterface):
    """
    Specific methods of chrome driver
    """

    def launch_app(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('launch_app')(*args, **kwargs)


class OperaWebDriverInterface(BaseInterface):
    """
    Specific methods of opera driver
    """
    pass


class FirefoxWebDriverInterface(BaseInterface):
    """
    Specific methods of firefox driver
    """

    @property
    def firefox_profile(self):
        return self.__getattr_from_webdriver_or_webelement__('firefox_profile')

    def set_context(self, *args, **kwargs):
        return self.__getattr_from_webdriver_or_webelement__('set_context')(*args, **kwargs)


class PhantomJSWebDriverInterface(BaseInterface):
    """
    Specific methods of phantomjs driver
    """
    pass


class IEWebDriverInterface(BaseInterface):
    """
    Specific methods of ie driver
    """
    pass


class WebDriverInterface(CommonWebDriverInterface,
                         ChromeWebDriverInterface,
                         OperaWebDriverInterface,
                         FirefoxWebDriverInterface,
                         PhantomJSWebDriverInterface,
                         IEWebDriverInterface):
    """
    Built interface for web driver.
    Class implemented provider interface
    to web driver instance for proxy object.
    """
    pass
