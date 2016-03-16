# -*- coding: utf-8 -*-

from selenium.webdriver.common.alert import Alert as _Alert
from selenium.webdriver.common.action_chains import ActionChains as _ActionChains
from selenium.webdriver.common.touch_actions import TouchActions as _TouchActions


class Alert(_Alert):

    def __init__(self, proxy):
        super(Alert, self).__init__(proxy.browser)

    @property
    def browser(self):
        return self.driver


class ActionChains(_ActionChains):

    def __init__(self, proxy):
        super(ActionChains, self).__init__(proxy.browser)

    @property
    def browser(self):
        return self._driver

    def reset(self):
        self._actions = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(ActionChains, self).__exit__(exc_type, exc_val, exc_tb)
        self.reset()


class TouchActions(_TouchActions):

    def __init__(self, proxy):
        super(TouchActions, self).__init__(proxy.browser)

    @property
    def browser(self):
        return self._driver

    def reset(self):
        self._actions = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(TouchActions, self).__exit__(exc_type, exc_val, exc_tb)
        self.reset()
