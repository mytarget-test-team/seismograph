# -*- coding: utf-8 -*-

from .exceptions import InvalidBindKey


_ENGINES = {}

_SESSION = None


def register_engine(bind_key, engine):
    _ENGINES[bind_key] = engine


def get_engine(bind_key):
    try:
        return _ENGINES[bind_key]
    except KeyError:
        raise InvalidBindKey(bind_key)


def register_session(session):
    global _SESSION
    _SESSION = session


def get_session():
    if _SESSION is None:
        raise RuntimeError('working outside session scope')

    return _SESSION
