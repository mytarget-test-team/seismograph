# -*- coding: utf-8 -*-

try:
    import httplib
except ImportError:
    import http.client as httplib

from threading import Lock

from flask import jsonify
from flask import request

from . import constants
from .mocks import BaseMock
from .tools import endpoint
from .mocks import get_mock_class_by_content_type


_add_mock_lock = Lock()


def make_response(status_code, *args, **kwargs):
    if args:
        resp = jsonify(results=args, count=len(args), **kwargs)
    else:
        resp = jsonify(kwargs)

    resp.status_code = int(status_code)
    return resp


def make_error_response(status_code, *errors):
    resp = jsonify({'errors': errors})
    resp.status_code = int(status_code)
    return resp


class MockerApi(object):

    def __init__(self, server):
        """
        :type server: seismograph.ext.mocker.server.MockServer
        """
        self.__server = server

    @property
    def url_rules(self):
        return {
            '/mocks/add': {
                'methods': ['POST'],
                'view_func': self.set_mock,
            },
            '/mocks/unblock': {
                'methods': ['POST'],
                'view_func': self.unblock_mock,
            },
            '/mocks/clean': {
                'methods': ['POST'],
                'view_func': self.clean_mocks,
            },
            '/status': {
                'methods': ['GET'],
                'view_func': self.get_status,
            },
        }

    def install(self):
        for url_rule, kwargs in self.url_rules.items():
            self.__server.add_url_rule(
                '{}{}'.format(constants.API_PATH, url_rule),
                **kwargs
            )

    def unblock_mock(self):
        data = request.json
        url_rule = data.get('url_rule')
        method = data.get('method', constants.DEFAULT_HTTP_METHOD)
        ep = endpoint(url_rule, method)

        if ep in self.__server.views:
            del self.__server.views[ep]

        return make_response(httplib.OK, status=constants.OK_STATUS)

    def set_mock(self):
        with _add_mock_lock:
            data = request.json
            url_rule = data.get('url_rule')

            if not url_rule:
                return make_error_response(httplib.BAD_REQUEST, '"url_rule" is required param')

            content_type = data.get('content_type')
            method = data.get('method', constants.DEFAULT_HTTP_METHOD)
            status = data.get('status', httplib.OK)
            headers = data.get('headers', {})
            body = data.get('body', '')

            if endpoint(url_rule, method) in self.__server.views:
                return make_response(httplib.OK, status=constants.MOCK_BLOCKED_STATUS)

            mock_cls = get_mock_class_by_content_type(content_type)

            self.__server.add_mock(
                mock_cls(
                    url_rule,
                    body=body,
                    headers=headers,
                    status_code=status,
                    http_method=method,
                    mime_type=content_type,
                    content_type=content_type,
                ),
            )

            return make_response(httplib.OK, status=constants.MOCK_ADDED_STATUS)

    def clean_mocks(self):
        for ep, view_func in self.__server.views.items():
            if isinstance(view_func, BaseMock):
                del self.__server.views[ep]

        return make_response(httplib.OK, status=constants.OK_STATUS)

    def get_status(self):
        data = {
            'host': self.__server.config.HOST,
            'port': self.__server.config.PORT,
            'debug': self.__server.config.DEBUG,
            'path_to_mocks': self.__server.config.PATH_TO_MOCKS,
            'static_folder': self.__server.config.STATIC_FOLDER,
            'static_url_path': self.__server.config.STATIC_URL_PATH,
            'block_timeout': self.__server.config.BLOCK_TIMEOUT,
            'urls': [ep for ep, mck in self.__server.views.items() if isinstance(mck, BaseMock)],
        }

        return make_response(httplib.OK, **data)
