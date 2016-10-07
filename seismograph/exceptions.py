# -*- coding: utf-8 -*-


class SeismographError(BaseException):

    def __init__(self, message=None, *args, **kwargs):
        message = message or ''

        super(SeismographError, self).__init__(message, *args, **kwargs)

        self.message = message  # please python 3


class Skip(SeismographError):
    pass


class LoaderError(SeismographError):
    pass


class ConfigError(SeismographError):
    pass


class EmergencyStop(SeismographError):
    pass


class CollectError(SeismographError):
    pass


class PyVersionError(SeismographError):
    pass


class TimeoutException(SeismographError):
    pass


class ExtensionNotFound(SeismographError):
    pass


class ExtensionNotRequired(SeismographError):
    pass


class DependencyError(SeismographError):
    pass


ALLOW_RAISED_EXCEPTIONS = (
    EmergencyStop,
    KeyboardInterrupt,
)
