# -*- coding: utf-8 -*-

"""
Multiprocessing utils
"""


class MPSupportedValue(object):

    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        val = getattr(self._value, 'value', None)
        if val is not None:
            return self._value.value

        return self._value

    @value.setter
    def value(self, value):
        if hasattr(self._value, 'value'):
            self._value.value = value
        else:
            self._value = value

    def set(self, value):
        self._value = value
