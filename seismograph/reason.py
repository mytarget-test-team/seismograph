# -*- coding: utf-8 -*-

from . import runnable
from .utils import pyv


def format_reason(reason):
    return reason.__format_reason__()


def format_reason_to_output(reason):
    return reason.__format_reason_to_output__()


class Reason(object):

    def __init__(self, runnable_object, reason, config):
        self.__config = config
        self.__runnable_object = runnable_object
        self.__reason = pyv.unicode_string(reason)

    @property
    def runnable_object(self):
        return self.__runnable_object

    @property
    def reason(self):
        return self.__reason

    @property
    def config(self):
        return self.__config

    def __format_reason__(self):
        if self.__runnable_object.__create_reason__:
            formatted_reason = (
                runnable.reason(self.__runnable_object),
                self.__reason,
            )
        else:
            formatted_reason = (
                self.__reason,
            )

        return u''.join(formatted_reason)

    def __format_reason_to_output__(self):
        tmp = []

        runnable_repr = repr(self.__runnable_object)
        sep_line = ''.join(
            '=' for _ in pyv.xrange(
                len(runnable_repr),
            ),
        )

        tmp.append(sep_line)
        tmp.append(runnable_repr)
        tmp.append(sep_line)
        tmp.append(self.__reason)

        return u'\n'.join(tmp)


def create(runnable_object, reason, config=None):
    return Reason(runnable_object, reason, config)


def item(name, desc, *args):
    return u'{} ({}): \n{}\n\n'.format(
        name, desc, u'\n'.join(u'  {}'.format(s) for s in args),
    )


def join(*args):
    def gen(item):
        for i in item:
            if isinstance(i, (list, tuple)):
                for ni in gen(i):
                    yield pyv.unicode_string(ni)
            else:
                yield pyv.unicode_string(i)

    return u''.join(gen(args))
