# -*- coding: utf-8 -*-

import os
import time
import logging
from contextlib import contextmanager

import requests
from flask import Flask as _Flask

from . import patch
from . import mock as _mock
from .exceptions import MockServerError
from .exceptions import MockServerClientError


APP_NAME = 'mocker'

DEFAULT_PORT = 5000
DEFAULT_HOST = '127.0.0.1'

DEFAULT_START_SERVER_TIMEOUT = 10


# Patch flask
Flask = type(
    'Flask',
    (_Flask, ),
    {
        'add_url_rule': patch.add_url_rule,
    },
)


def set_log_level_for_dependency(debug):
    loggers = (
        logging.getLogger('flask'),
        logging.getLogger('werkzeug'),
    )

    handlers = {
        False: logging.NullHandler,
        True: logging.StreamHandler,
    }

    for logger in loggers:
        logger.handlers = []
        logger.handlers.append(handlers[bool(debug)]())
        logger.setLevel(logging.INFO if debug else logging.ERROR)


class MockServerClient(object):

    ALLOW_HTTP_METHODS = (
        'get',
        'put',
        'head',
        'post',
        'patch',
        'delete',
        'options',
    )

    def __init__(self, server):
        self.__server = server

    def __getattr__(self, http_method):
        if http_method not in self.ALLOW_HTTP_METHODS:
            raise MockServerClientError(
                'Incorrect http method for request: "{}"'.format(http_method),
            )

        method = getattr(requests, http_method)

        def method_wrapper(path, *args, **kwargs):
            return method(
                'http://{}:{}{}'.format(
                    self.__server.host,
                    self.__server.port,
                    path,
                ),
                *args, **kwargs
            )

        return method_wrapper


class BaseMockServer(object):

    __mock_class__ = _mock.BaseMock
    __file_extensions__ = ('.resp', )

    def __init__(self,
                 mock_path=None,
                 host=None,
                 port=None,
                 mocks=None,
                 debug=False,
                 gevent=False,
                 threading=False,
                 multiprocessing=False):
        set_log_level_for_dependency(debug)

        self.__app = Flask(APP_NAME)
        self.__app.debug = debug

        self.__debug = debug
        self.__host = host or DEFAULT_HOST
        self.__port = port or DEFAULT_PORT

        self._gevent = gevent
        self._threading = threading
        self._multiprocessing = multiprocessing

        if not threading and not gevent and not multiprocessing:
            self._threading = True

        self._process = None
        self._started = False
        self._client = MockServerClient(self)

        if mock_path:
            self.scan_dir(mock_path)

        if mocks:
            for mock in mocks:
                self.add_mock(mock)

    def __call__(self, *args, **kwargs):
        return self.wsgi_handler(*args, **kwargs)

    @property
    def _stopped(self):
        return not self._started

    @property
    def views(self):
        return self.__app.view_functions

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

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
            if isinstance(v, _mock.BaseMock)
        )

    @property
    def wsgi_handler(self):
        return self.__app.wsgi_app

    def scan_dir(self, mock_path):
        for name in os.listdir(mock_path):
            path = os.path.join(mock_path, name)

            if any(name.endswith(ex) for ex in self.__file_extensions__):
                with open(path, 'r') as fp:
                    mock = self.__mock_class__(path, None)
                    _mock.on_file(mock, fp)
                self.add_mock(mock)

            if os.path.isdir(path):
                self.scan_dir(path)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        self.__app.add_url_rule(
            rule, endpoint=endpoint, view_func=view_func, **options
        )

    def delete_mock(self, mock):
        try:
            del self.views[mock.endpoint]
        except KeyError:
            raise MockServerError(
                'Can\' delete mock "{}" because not exist'.format(mock),
            )

    def add_mock(self, mock, rewrite=False):
        """
        :type mock: BaseMock
        :type rewrite: bool
        """
        need_restart = self._started and self._multiprocessing

        if need_restart:
            self.stop()

        try:
            if rewrite:
                self.delete_mock(mock)
                self.add_mock(mock)
            else:
                self.add_url_rule(
                    mock.url_rule,
                    view_func=mock,
                    endpoint=mock.endpoint,
                    methods=[mock.http_method],
                )
        finally:
            if need_restart:
                self.start()

    @contextmanager
    def mock(self, mock):
        """
        :type mock: BaseMock
        """
        for old_mock in self.mocks:
            if old_mock == mock:
                with mock.as_(old_mock):
                    self.add_mock(mock, rewrite=True)
                try:
                    yield old_mock
                finally:
                    self.add_mock(old_mock, rewrite=True)
                break
        else:
            self.add_mock(mock)
            try:
                yield None
            finally:
                _mock.abort(mock, 404)

    def run(self):
        self.__app.run(host=self.__host, port=self.__port)

    def serve_forever(self):
        if self._gevent:
            from gevent.wsgi import WSGIServer

            WSGIServer(
                (self.__host, self.__port), self,
                log='default' if self.__debug else None,
            ).serve_forever()
        if self._threading:
            from werkzeug.serving import ThreadedWSGIServer

            ThreadedWSGIServer(self.__host, self.__port, self).serve_forever()
        if self._multiprocessing:
            from werkzeug.serving import ForkingWSGIServer

            ForkingWSGIServer(self.__host, self.__port, self).serve_forever()
        else:
            self.run()

    def waiting_for_ready(self, timeout=DEFAULT_START_SERVER_TIMEOUT):
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
                'Mock server have not been started for "{}" sec.'.format(timeout),
            )

    def start(self):
        if self._started:
            return

        if self._gevent:
            from .run_server.gevent import RunServerInGreenlet

            self._process = RunServerInGreenlet(self)
        elif self._threading:
            from werkzeug.serving import ThreadedWSGIServer
            from .run_server.threading import RunServerInThread

            self._process = RunServerInThread(self, ThreadedWSGIServer)
        elif self._multiprocessing:
            from werkzeug.serving import ForkingWSGIServer
            from .run_server.threading import RunServerInThread

            self._process = RunServerInThread(self, ForkingWSGIServer)
        else:
            raise MockServerError(
                'Can not start mock server. Don\'t know how :(.'
            )

        self._process.start()

        self._started = True
        self.waiting_for_ready()

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        if self._stopped:
            return

        if self._gevent:
            self._process.kill()
        elif self._threading:
            self._process.stop()
        elif self._multiprocessing:
            self._process.stop()
        else:
            raise MockServerError(
                'Can not stop mock server. Don\'t know how :(.'
            )

        self._process.join()

        self._process = None
        self._started = False
