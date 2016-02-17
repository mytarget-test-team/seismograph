# -*- coding: utf-8 -*-

from ...exceptions import SeismographError


class MockServerError(SeismographError):
    pass


class MockServerClientError(MockServerError):
    pass
