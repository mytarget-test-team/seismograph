# -*- coding: utf-8 -*-

from ...exceptions import SeismographError


class MockerError(SeismographError):
    pass


class MockServerError(MockerError):
    pass


class MockServerClientError(MockerError):
    pass
