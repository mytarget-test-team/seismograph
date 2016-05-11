# -*- coding: utf-8 -*-

from seismograph.case import (
    Case,
    MountData,
)


class FakeCase(Case):

    __mount_data__ = MountData(__name__)

    def test(self):
        pass


def mark_is_run(case):
    case.__is_run__ = lambda: True


def create(*args, **kwargs):
    return FakeCase('test', *args, **kwargs)
