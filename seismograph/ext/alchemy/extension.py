# -*- coding: utf-8 -*-

from contextlib import contextmanager

from . import registry
from .constants import DEFAULT_BIND_KEY


EX_NAME = 'db'


class DBClient(object):
    """
    Read-write client
    """

    def __call__(self, bind_key=DEFAULT_BIND_KEY, model=None):
        if model:
            return model.bind_key(bind_key)
        return self.get_connection(bind_key)

    @staticmethod
    def get_connection(bind_key=DEFAULT_BIND_KEY):
        return registry.get_engine(bind_key).connect()

    @contextmanager
    def read(self, bind_key=DEFAULT_BIND_KEY):
        yield self.get_connection(bind_key).execute

    @contextmanager
    def write(self, bind_key=DEFAULT_BIND_KEY):
        connection = self.get_connection(bind_key)
        trans = connection.begin()
        try:
            yield connection.execute
            trans.commit()
        except BaseException as error:
            trans.rollback()
            raise error
