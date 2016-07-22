# -*- coding: utf-8 -*-

import re
import json

from flask import Response

from ...utils import pyv
from . import constants

if pyv.IS_PYTHON_2:
    import urlparse
else:
    from urllib import parse


CLEAN_DATA_REGEXP = re.compile(r'^\s{2}|\n|\r$')


def on_file(mock, fp):
    mock.__on_file__(fp)


def parse_meta_data(string):
    http_method, status_code, url_rule = [
        item.strip() for item in string.split(' ')
    ]
    return http_method, status_code, url_rule


def parse_header(string):
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
                 url_rule=None,
                 body=None,
                 headers=None,
                 mime_type=None,
                 status_code=None,
                 http_method=None,
                 content_type=None):
        self._body = body or ''
        self._url_rule = url_rule
        self._mime_type = mime_type
        self._headers = headers or {}
        self._content_type = content_type
        self._status_code = status_code or constants.DEFAULT_STATUS_CODE
        self._http_method = http_method or constants.DEFAULT_HTTP_METHOD

        if self.__headers__:
            for k, v in self.__headers__.items():
                self._headers.setdefault(k, v)

    def __call__(self, *args, **kwargs):
        return self.make_response()

    def __repr__(self):
        return '<ResponseProvider(url_rule={} http_method={})>'.format(
            self.url_rule, self.http_method,
        )

    def __eq__(self, other):
        compare = (
            self.url_rule == other.url_rule,
            self.http_method == other.http_method,
        )
        return all(compare)

    def __on_file__(self, fp):
        body = []

        meta_was_found = False
        break_line_was_found = False

        break_line_chars = ('\n', '\r', '\r\n')

        lines = [l for l in fp.readlines()]

        can_find_meta = lambda: (
            not meta_was_found
        )
        can_find_header = lambda: (
            meta_was_found
            and
            not break_line_was_found
        )
        can_find_break_line = lambda: (
            not break_line_was_found
            and
            meta_was_found
        )

        for line in lines:
            try:
                line = line.decode('utf-8')
            except AttributeError:  # please python 3 :)
                pass

            if line.startswith('#'):  # pass comment line
                continue

            if can_find_break_line():
                if line.replace(' ', '') in break_line_chars:
                    break_line_was_found = True

            if can_find_meta() and self.META_REGEXP.search(line):
                http_method, status_code, url_rule = parse_meta_data(line)
                self._url_rule = url_rule
                self._http_method = http_method
                self._status_code = status_code
                meta_was_found = True
            elif can_find_header() and self.HEADER_REGEXP.search(line):
                key, value = parse_header(line)
                self._headers[key] = value
            else:
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

    def make_response(self):
        return Response(
            self.body,
            headers=self.headers,
            mimetype=self.mime_type,
            status=self.status_code,
            content_type=self.content_type,
        )


class JsonMock(BaseMock):

    __mime_type__ = 'application/json'
    __content_type__ = 'application/json'

    @property
    def body(self):
        return json.dumps(self._body)

    @property
    def json(self):
        return self._body

    def __on_file__(self, fp):
        super(JsonMock, self).__on_file__(fp)

        # for pre validation only
        self._body = json.loads(
            CLEAN_DATA_REGEXP.sub('', self._body),
        )


class HTMLMock(BaseMock):

    __mime_type__ = 'text/html'
    __content_type__ = 'text/html'


DEFAULT_MOCK_CLASS = BaseMock

CONTENT_TYPE_TO_MOCK_CLASS = {
    'text/html': HTMLMock,
    'application/json': JsonMock,
}

FILE_EXTENSION_TO_MOCK_CLASS = {
    'json': JsonMock,
    'html': HTMLMock,
}


def get_mock_class_by_file_name(filename):
    """
    :rtype: BaseMock
    """
    split_name = filename.replace('.mock', '').split('.')
    try:
        ext = split_name[len(split_name) - 1]
        return FILE_EXTENSION_TO_MOCK_CLASS.get(ext, DEFAULT_MOCK_CLASS)
    except IndexError:
        return DEFAULT_MOCK_CLASS


def get_mock_class_by_content_type(content_type):
    """
    :rtype: BaseMock
    """
    return CONTENT_TYPE_TO_MOCK_CLASS.get(content_type, DEFAULT_MOCK_CLASS)
