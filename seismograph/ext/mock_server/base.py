# -*- coding: utf-8 -*-

import os
import re
import time
import logging
from contextlib import contextmanager

import requests
from flask import Response
from flask import abort as _abort
from flask import Flask as _Flask

from . import path


APP_NAME = 'mocker'
ABORT_ATTRIBUTE_NAME = '__abort__'

DEFAULT_PORT = 5000
DEFAULT_HOST = '127.0.0.1'

DEFAULT_STATUS_CODE = 200
DEFAULT_HTTP_METHOD = 'GET'

DEFAULT_START_SERVER_TIMEOUT = 10


# Patch flask
Flask = type(
    'Flask',
    (_Flask, ),
    {
        'add_url_rule': path.add_url_rule,
    },
)


def on_file(mock, fp):
    mock.__on_file__(fp)


def abort(mock, status_code):
    setattr(mock, ABORT_ATTRIBUTE_NAME, status_code)


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


def parse_for_meta(string):
    http_method, status_code, url_rule = [
        item.strip() for item in string.split(' ')
    ]
    return http_method, status_code, url_rule


def parse_for_header(string):
    key = string[:string.index(':'):]
    value = string[string.index(':') + 1:]

    return key.strip(), value.strip()


class MockServerError(BaseException):
    pass


class MockServerClientError(BaseException):
    pass


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


class BaseMock(object):

    __headers__ = None
    __mime_type__ = None
    __content_type__ = None

    HEADER_REGEXP = re.compile(r'[A-z -]+:.*\s')
    META_REGEXP = re.compile(r'[A-Z]{3,6}\s[0-9]{3}\s\/.*\s')

    def __init__(self,
                 endpoint,
                 url_rule,
                 body=None,
                 headers=None,
                 mime_type=None,
                 status_code=None,
                 http_method=None,
                 content_type=None):
        self._body = body or ''
        self._url_rule = url_rule
        self._endpoint = endpoint
        self._mime_type = mime_type
        self._headers = headers or {}
        self._content_type = content_type
        self._status_code = status_code or DEFAULT_STATUS_CODE
        self._http_method = http_method or DEFAULT_HTTP_METHOD

        if self.__headers__:
            for k, v in self.__headers__:
                self._headers.setdefault(k, v)

    def __call__(self, *args, **kwargs):
        abort_code = getattr(
            self, ABORT_ATTRIBUTE_NAME, None,
        )

        if abort_code:
            _abort(abort_code)

        return self.make_response()

    def __repr__(self):
        return '<ResponseProvider(url_rule={} http_method={}): {}>'.format(
            self.url_rule, self.http_method, self.endpoint,
        )

    def __eq__(self, other):
        compare = (
            self.url_rule == other.url_rule,
            self.http_method == other.http_method,
        )
        return all(compare)

    def __on_file__(self, fp):
        body = []

        for line in fp.readlines():
            try:
                line = line.decode('utf-8')
            except AttributeError:  # please python 3 :)
                pass

            if line.startswith('#'):  # pass comment line
                continue

            if self.HEADER_REGEXP.search(line):
                key, value = parse_for_header(line)
                self._headers[key] = value
            elif self.META_REGEXP.search(line):
                http_method, status_code, url_rule = parse_for_meta(line)
                self._url_rule = url_rule
                self._http_method = http_method
                self._status_code = status_code
            else:
                # Other line as body item
                body.append(line)

        self._body = u''.join(body)

    @property
    def body(self):
        return self._body

    @property
    def headers(self):
        return self._headers

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def url_rule(self):
        return self._url_rule

    @property
    def status_code(self):
        return int(self._status_code)

    @property
    def http_method(self):
        return self._http_method.upper()

    @property
    def mime_type(self):
        return self._mime_type or self.__mime_type__

    @property
    def content_type(self):
        return self._content_type or self.__content_type__

    @contextmanager
    def as_(self, mock):
        assert self == mock

        endpoint = self._endpoint
        self._endpoint = mock.endpoint
        try:
            yield
        finally:
            self._endpoint = endpoint

    def make_response(self):
        return Response(
            self.body,
            headers=self.headers,
            mimetype=self.mime_type,
            status=self.status_code,
            content_type=self.content_type,
        )


class BaseMockServer(object):

    __mock_class__ = BaseMock
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
            if isinstance(v, BaseMock)
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
                    on_file(mock, fp)
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
                    yield
                finally:
                    self.add_mock(old_mock, rewrite=True)
                break
        else:
            self.add_mock(mock)
            try:
                yield
            finally:
                abort(mock, 404)

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
