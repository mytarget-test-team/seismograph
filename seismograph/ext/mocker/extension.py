# -*- coding: utf-8 -*-

from .server import MockServer


class Config(object):

    def __init__(self,
                 host=None,
                 port=None,
                 mocks=None,
                 debug=False,
                 gevent=False,
                 path_to_mocks=None,
                 static_folder=None,
                 static_url_path=None,
                 block_timeout=None):
        self.HOST = host
        self.PORT = port
        self.DEBUG = debug
        self.GEVENT = gevent
        self.PATH_TO_MOCKS = path_to_mocks
        self.STATIC_FOLDER = static_folder
        self.STATIC_URL_PATH = static_url_path
        self.BLOCK_TIMEOUT = block_timeout


class Mocker(object):

    __server_class__ = MockServer

    def __init__(self, config):
        """
        :type config: Config
        """
        self.__config = config

        self.__server = self.__server_class__(config)

    @property
    def config(self):
        return self.__config

    def start(self):
        return self.__server.start()

    def stop(self):
        return self.__server.stop()

    def restart(self):
        self.__server.restart()

    def add_mock(self, *args, **kwargs):
        return self.__server.client.add_mock(*args, **kwargs)

    def unblock_mock(self, *args, **kwargs):
        return self.__server.client.unblock_mock(*args, **kwargs)

    def clean_mocks(self):
        return self.__server.client.clean_mocks()
