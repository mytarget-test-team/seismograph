# -*- coding: utf-8 -*-

import sys
from functools import wraps
from collections import OrderedDict
from contextlib import contextmanager

from .utils import pyv
from .utils.mp import MPSupportedValue


def run(runnable, *args, **kwargs):
    return runnable.__run__(*args, **kwargs)


def reason(runnable):
    return runnable.__reason__()


def stopped_on(runnable, method_name=None):
    if method_name:
        runnable._stopped_on = method_name
        return method_name

    return runnable.__stopped_on__()


def set_debug_if_allowed(config):
    if config.PDB:
        _, _, tb = sys.exc_info()

        try:
            import ipdb as pdb
        except ImportError:
            import pdb

        pdb.post_mortem(tb)


def is_run(runnable):
    return runnable.__is_run__()


def is_mount(runnable):
    assert issubclass(runnable.__class__, MountObjectMixin), \
        '"{}" is not mount object'.format(runnable.__class__)
    return runnable.__is_mount__()


def is_build(runnable):
    assert issubclass(runnable.__class__, BuildObjectMixin), \
        '"{}" is not build object'.format(runnable.__class__)
    return runnable.__is_build__()


def method_name(runnable):
    return runnable.__method_name__()


def class_name(runnable):
    return runnable.__class_name__()


def run_method(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        assert is_run(self), 'Can not call "{}" of "{}.{}". Should be run.'.format(
            pyv.get_func_name(f), self.__class__.__module__, self.__class__.__name__,
        )
        return f(self, *args, **kwargs)
    return wrapper


def mount_method(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        assert is_mount(self), 'Can not call "{}" of "{}.{}". Should be mount.'.format(
            pyv.get_func_name(f), self.__class__.__module__, self.__class__.__name__,
        )
        return f(self, *args, **kwargs)
    return wrapper


def build_method(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        assert is_build(self), 'Can not call "{}" of "{}.{}". Should be built.'.format(
            pyv.get_func_name(f), self.__class__.__module__, self.__class__.__name__,
        )
        return f(self, *args, **kwargs)
    return wrapper


class RunnableObject(object):

    __create_reason__ = False

    def __init__(self):
        self.__id = id(self)
        self.__stopped_on = MPSupportedValue(
            method_name(self),
        )
        self.__reason_storage = OrderedDict()

    def __call__(self, *args, **kwargs):
        return self.__run__(*args, **kwargs)

    def __repr__(self):
        class_path = '{}.{}'.format(
            self.__class__.__module__, self.__class__.__name__,
        )
        return '<{} method_name={} stopped_on={}>'.format(
            class_path, method_name(self), stopped_on(self),
        )

    @property
    def id(self):
        return self.__id

    @property
    def _stopped_on(self):
        return self.__stopped_on.value

    @_stopped_on.setter
    def _stopped_on(self, value):
        self.__stopped_on.value = value

    @property
    def reason_storage(self):
        return self.__reason_storage

    def __is_run__(self):
        raise NotImplementedError(
            'Method "__is_run__" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def __method_name__(self):
        return 'run'

    def __stopped_on__(self):
        return self._stopped_on

    def __class_name__(self):
        return '{}.{}'.format(
            self.__class__.__module__, self.__class__.__name__,
        )

    def __reason__(self):
        return 'Your reason can be here. This is from "{}.{}.__reason__" method.\n'.format(
            self.__class__.__module__, self.__class__.__name__,
        )

    def __run__(self, *args, **kwargs):
        raise NotImplementedError(
            'Method "run" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def support_mp(self, manager):
        self.__stopped_on.set(
            manager.Value('s', self._stopped_on),
        )


class BuildObjectMixin(object):

    def __is_build__(self):
        raise NotImplementedError(
            'Method "__is_mount__" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )


class MountObjectMixin(object):

    def __is_mount__(self):
        raise NotImplementedError(
            'Method "__is_mount__" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )


class ContextOfRunnableObject(object):

    @contextmanager
    def __call__(self, runnable):
        self.start_context(runnable)
        try:
            yield
        finally:
            if stopped_on(runnable) != 'start_context':
                self.stop_context(runnable)

    @property
    def layers(self):
        raise NotImplementedError(
            'Property "layers" is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    @property
    def setup_callbacks(self):
        raise NotImplementedError(
            'Property "setup_callbacks" is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    @property
    def teardown_callbacks(self):
        raise NotImplementedError(
            'Property "teardown_callbacks" is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def start_context(self, obj):
        raise NotImplementedError(
            'Method "start_context" is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def stop_context(self, obj):
        raise NotImplementedError(
            'Method "stop_context" is not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )


class LayerOfRunnableObject(object):

    def __init__(self):
        self.enabled = True


class RunnableGroup(RunnableObject):

    def __init__(self, objects, config):
        super(RunnableGroup, self).__init__()

        self.__objects = objects
        self.__config = config

        self._is_run = False

    def __is_run__(self):
        return self._is_run

    @property
    def config(self):
        return self.__config

    @property
    def objects(self):
        return self.__objects
