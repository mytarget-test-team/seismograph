# -*- coding: utf-8 -*-

from functools import wraps
from contextlib import contextmanager

import requests

from . import constants
from .exceptions import MockerError
from ...utils.common import waiting_for
from .exceptions import MockServerClientError


instance = None


def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.ConnectionError:
            raise MockerError('Mock server was not started')
    return wrapper


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

    def __init__(self, config):
        """
        :type config: seismograph.ext.mocker.extension.Config
        """
        global instance
        instance = self

        self.__config = config

    def __getattr__(self, http_method):
        if http_method not in self.ALLOW_HTTP_METHODS:
            raise MockServerClientError(
                'Incorrect http request method: "{}"'.format(http_method),
            )

        method = getattr(requests, http_method)

        def method_wrapper(path, *args, **kwargs):
            return method(
                'http://{}:{}{}'.format(
                    self.__config.HOST,
                    self.__config.PORT,
                    path,
                ),
                *args, **kwargs
            )

        return method_wrapper

    @property
    def config(self):
        return self.__config

    @contextmanager
    @handle_errors
    def path(self, url_rule, **kwargs):
        self.add_mock(url_rule, **kwargs)
        try:
            yield
        finally:
            self.unblock_mock(url_rule, method=kwargs.get('method'))

    @handle_errors
    def add_mock(self,
                 url_rule,
                 body=None,
                 json=None,
                 html=None,
                 status=None,
                 method=None,
                 headers=None,
                 content_type=None):
        data = {'url_rule': url_rule}

        if method:
            data['method'] = method

        if headers:
            data['headers'] = headers

        if json:
            data['content_type'] = 'application/json'
        elif html:
            data['content_type'] = 'text/html'
        elif content_type:
            data['content_type'] = content_type

        if status:
            data['status'] = status

        data['body'] = body or json or html or ''

        def was_added(resp):
            d = resp.json()
            return d.get('status') == constants.MOCK_ADDED_STATUS

        get_resp = lambda: self.post('/mocker/api/mocks/add', json=data)

        return waiting_for(
            lambda: was_added(get_resp()),
            delay=0.5,
            timeout=self.__config.BLOCK_TIMEOUT,
            message='Can not add mock to url rule "{}" already exist'.format(url_rule),
        )

    @handle_errors
    def unblock_mock(self, url_rule, method=None):
        def was_unblocked(resp):
            d = resp.json()
            return d.get('status') == constants.OK_STATUS

        return was_unblocked(
            self.post(
                '/mocker/api/mocks/unblock',
                json={
                    'url_rule': url_rule,
                    'method': method or constants.DEFAULT_HTTP_METHOD,
                },
            ),
        )

    @handle_errors
    def clean_mocks(self):
        def was_cleaned(resp):
            d = resp.json()
            return d.get('status') == constants.OK_STATUS

        return was_cleaned(
            self.post(
                '/mocker/api/mocks/clean',
            )
        )
