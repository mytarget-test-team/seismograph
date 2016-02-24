# -*- coding: utf-8 -*-

import re
from contextlib import contextmanager

from flask import Response
from flask import abort as _abort

from ...utils import pyv

if pyv.IS_PYTHON_2:
    import urlparse
else:
    from urllib import parse


DEFAULT_STATUS_CODE = 200
DEFAULT_HTTP_METHOD = 'GET'

ABORT_ATTRIBUTE_NAME = '__abort__'


def on_file(mock, fp):
    mock.__on_file__(fp)


def abort(mock, status_code):
    setattr(mock, ABORT_ATTRIBUTE_NAME, status_code)


def parse_for_meta(string):
    http_method, status_code, url_rule = [
        item.strip() for item in string.split(' ')
    ]
    return http_method, status_code, url_rule


def parse_for_header(string):
    key = string[:string.index(':'):]
    value = string[string.index(':') + 1:]

    return key.strip(), value.strip()


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

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as fp:
            mock = cls(file_path, None)
            on_file(mock, fp)
        return mock

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
    def params(self):
        if pyv.IS_PYTHON_2:
            return urlparse.parse_qs(
                urlparse.urlparse(self.url_rule).query,
            )
        return parse.parse_qs(
            parse.urlparse(self._url_rule).query,
        )

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
