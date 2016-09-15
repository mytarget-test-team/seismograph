# -*- coding: utf-8 -*-

try:
    import httplib
except ImportError:
    import http.client as httplib


EX_NAME = 'mocker'
CONFIG_KEY = 'MOCKER_EX'

API_PATH = '/mocker/api'

WSGI_APP_NAME = 'mocker'

DEFAULT_PORT = 5000
DEFAULT_HOST = '127.0.0.1'

DEFAULT_HTTP_METHOD = 'GET'
DEFAULT_STATUS_CODE = httplib.OK

DEFAULT_START_SERVER_TIMEOUT = 10
DEFAULT_BLOCK_TIMEOUT = 60 * 3

OK_STATUS = 'ok'
MOCK_ADDED_STATUS = 'added'
MOCK_BLOCKED_STATUS = 'blocked'

DEFAULT_STATIC_FOLDER = 'static'
DEFAULT_STATIC_URL_PATH = '/static'
