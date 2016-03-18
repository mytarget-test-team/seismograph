# -*- coding: utf-8 -*-

from .webdriver import WebDriverInterface
from .webelement import WebElementInterface
from .base import HTML_TAGS_ALLOWED_AS_METHOD


__all__ = (
    'WebDriverInterface',
    'WebElementInterface',
    'HTML_TAGS_ALLOWED_AS_METHOD',
)
