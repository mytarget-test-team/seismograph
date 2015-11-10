# -*- coding: utf-8 -*-

from .selenium import SeleniumExtension
from .mock_server import MockServerExtension


EXTENSIONS = (
    SeleniumExtension,
    MockServerExtension,
)
