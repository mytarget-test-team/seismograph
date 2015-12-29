# -*- coding: utf-8 -*-

from ...exceptions import SeismographError


class SeleniumExError(SeismographError):
    pass


class PollingTimeoutExceeded(SeleniumExError):
    pass


class RouterError(SeleniumExError):
    pass


class RouteNotFound(RouterError):
    pass


class ReRaiseException(SeleniumExError):
    pass


class FieldError(SeleniumExError):
    pass
