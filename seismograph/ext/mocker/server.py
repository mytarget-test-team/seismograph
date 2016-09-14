# -*- coding: utf-8 -*-

import os
import time
from threading import Lock

import requests
from flask import Flask as _Flask

from . import patch
from . import constants
from .mocks import BaseMock
from .tools import endpoint
from .client import MockServerClient
from .exceptions import MockServerError
from .mocks import get_mock_class_by_file_name
from .tools import set_log_level_for_dependency
from .mocks import on_file as fill_mock_from_file


MOCK_FILE_EXTENSION = '.mock'


# Patch flask
Flask = type(
    'Flask',
    (_Flask, ),
    {
        'add_url_rule': patch.add_url_rule,
        'dispatch_request': patch.dispatch_request(
            _Flask.dispatch_request,
        ),
    },
)


lock = Lock()


class MockServer(object):

    __client_class__ = MockServerClient

    def __init__(self, config):
        """
        :type config: seismograph.ext.mocker.extension.Config
        """
        set_log_level_for_dependency(config.DEBUG)

        self.__app = Flask(
            constants.WSGI_APP_NAME,
            static_url_path=config.STATIC_URL_PATH,
            static_folder=config.STATIC_FOLDER
        )
        self.__app.debug = config.DEBUG

        self.__config = config
        self.__debug = config.DEBUG

        self._process = None
        self._started = False
        self._client = self.__client_class__(config)

        if config.PATH_TO_MOCKS:
            self.scan_dir(config.PATH_TO_MOCKS)

        with self.__app.app_context():
            from .api import MockerApi
            MockerApi(self).install()

    def __call__(self, *args, **kwargs):
        return self.wsgi_handler(*args, **kwargs)

    @property
    def _stopped(self):
        return not self._started

    @property
    def views(self):
        return self.__app.view_functions

    @property
    def config(self):
        return self.__config

    @property
    def client(self):
        return self._client

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = value
        self.__app.debug = value
        set_log_level_for_dependency(value)

    @property
    def mocks(self):
        return (
            v for v in self.views.values()
            if isinstance(v, BaseMock)
        )

    @property
    def wsgi_handler(self):
        return self.__app.wsgi_app

    def scan_dir(self, mock_path):
        for name in os.listdir(mock_path):
            path = os.path.join(mock_path, name)

            if name.endswith(MOCK_FILE_EXTENSION):
                with open(path, 'r') as fp:
                    mock_cls = get_mock_class_by_file_name(name)
                    mock = mock_cls()
                    fill_mock_from_file(mock, fp)
                self.add_mock(mock)

            if os.path.isdir(path):
                self.scan_dir(path)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        with lock:
            self.__app.add_url_rule(
                rule, endpoint=endpoint, view_func=view_func, **options
            )

    def add_mock(self, mock):
        """
        :type mock: BaseMock
        :type rewrite: bool
        """
        self.add_url_rule(
            mock.url_rule,
            view_func=mock,
            endpoint=endpoint(
                mock.url_rule,
                mock.http_method,
            ),
            methods=[mock.http_method],
        )

    def run(self):
        self.__app.run(host=self.__config.HOST, port=self.__config.PORT)

    def serve_forever(self):
        if self.__config.GEVENT:
            from gevent.wsgi import WSGIServer

            WSGIServer(
                (self.__config.HOST, self.__config.PORT), self,
                log='default' if self.__debug else None,
            ).serve_forever()
        else:
            from werkzeug.serving import ThreadedWSGIServer

            ThreadedWSGIServer(self.__config.HOST, self.__config.PORT, self).serve_forever()

    def waiting_for_ready(self, timeout=constants.DEFAULT_START_SERVER_TIMEOUT):
        if self._stopped:
            raise MockServerError('Mock server is not started')

        is_error = True
        t_start = time.time()

        while time.time() <= t_start + timeout:
            if not is_error:
                break

            try:
                self._client.get('/')
                is_error = False
            except requests.ConnectionError:
                pass

        if is_error:
            raise MockServerError(
                'Mock server has not been started for "{}" sec.'.format(timeout),
            )

    def start(self):
        if self._started:
            return

        if self.__config.GEVENT:
            from .runners.gevent import RunServerInGreenlet

            self._process = RunServerInGreenlet(self)
        else:
            from werkzeug.serving import ThreadedWSGIServer
            from .runners.threading import RunServerInThread

            self._process = RunServerInThread(self, ThreadedWSGIServer)

        self._process.start()

        self._started = True
        self.waiting_for_ready()

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        if self._stopped:
            return

        if self.__config.GEVENT:
            self._process.kill()
        else:
            self._process.stop()

        self._process.join()

        self._process = None
        self._started = False
