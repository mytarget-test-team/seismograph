# -*- coding: utf-8 -*-

"""
Extension for mock http external resources.

Usage:

    from seismograph.ext import mocker


    with mocker.path('/users/<int:id>', json={'name': 'Username'}):
        pass

    @mocker.mock('/user/<int:id>', json={'name': 'Username'})
    def do_something():
        pass


    some_api = mocker.declare_external_resource('/some/api')


    with some_api.path('/users/<int:id>', json={'name': 'Username'}):
        pass

    @some_api.mock('/user/<int:id>', json={'name': 'Username'})
    def do_something(case):
        pass

    # or

    @some_api('/user/<int:id>', json={'name': 'Username'})
    def do_something(case):
        pass


    # You can to run server from program instance

    import seismograph


    class Program(seismograph.Program):

        def setup(self):
            self.ext('mocker').start()

        def teardown(self):
            self.ext('mocker').stop()


    # or from command line interface like:
    # seismograph.mocker --help
    # or
    # python -m seismograph.ext.mocker --help
    #
    # Should to know:
    # Server have to run when you can try to mock url,
    # also your application should to know about mock server URL.


Need to require mocker where it using
"""

from functools import wraps
from optparse import OptionGroup

from . import client as _client
from . import constants as _constants
from .extension import Config as _Config
from .extension import Mocker as _Mocker


class _MockResource(object):

    def __init__(self, base_path):
        self._base_path = base_path

    def __call__(self, *args, **kwargs):
        return self.mock(*args, **kwargs)

    def _compile_url_rule(self, url_rule):
        return '{}{}'.format(self._base_path, url_rule).replace('//', '/')

    def mock(self, url_rule, **params):
        return mock(self._compile_url_rule(url_rule), **params)

    def path(self, url_rule, **kwargs):
        """
        Contextmanager will be returned
        """
        return _client.instance.path(self._compile_url_rule(url_rule), **kwargs)

    def add_mock(self, url_rule, **kwargs):
        return _client.instance.add_mock(self._compile_url_rule(url_rule), kwargs)

    def unblock_mock(self, url_rule):
        return _client.instance.unblock_mock(self._compile_url_rule(url_rule))

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__, self._base_path,
        )


def declare_external_resource(base_path=None):
    return _MockResource(base_path or '')


def mock(url_rule, **params):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            with _client.instance.path(url_rule, **params):
                result = f(*args, **kwargs)
            return result
        return wrapped
    return wrapper


def get_current_url():
    if _client.instance is not None:
        return 'http://{}:{}'.format(_client.instance.config.HOST, _client.instance.config.PORT)

    raise RuntimeError('Working outside mocker context')


def get_current_static_url():
    return '{}{}'.format(get_current_url(), _client.instance.config.STATIC_URL_PATH)


def path(url_rule, **params):
    """
    Contextmanager will be returned
    """
    return _client.instance.path(url_rule, **params)


def unblock(url_rule, method):
    return _client.instance.unblock_mock(url_rule, method)


def __add_options__(parser):
    group = OptionGroup(parser, 'MockServer extension options')

    group.add_option(
        '--mocker-path-to-mocks',
        dest='MOCKER_PATH_TO_MOCKS',
        default=None,
        help='Path to dir within mock files.'
    )
    group.add_option(
        '--mocker-host',
        dest='MOCKER_HOST',
        default=None,
        help='Server host.',
    )
    group.add_option(
        '--mocker-port',
        dest='MOCKER_PORT',
        default=None,
        type=int,
        help='Server port.',
    )
    group.add_option(
        '--mocker-block-timeout',
        dest='MOCKER_BLOCK_TIMEOUT',
        default=None,
        type=float,
        help='Timeout to set mock if exist.',
    )
    group.add_option(
        '--mocker-debug',
        dest='MOCKER_DEBUG',
        action='store_true',
        default=False,
        help='Use debug.',
    )
    group.add_option(
        '--mocker-static-folder',
        dest='MOCKER_STATIC_FOLDER',
        default=None,
        help='Path to dir within mock static files.',
    )
    group.add_option(
        '--mocker-static-path',
        dest='MOCKER_STATIC_URL_PATH',
        default=None,
        help='Path for static files on the web.',
    )

    parser.add_option_group(group)


def __install__(program):
    params = program.config.get(_constants.CONFIG_KEY, {})

    config = _Config(
        host=program.config.MOCKER_HOST or params.get('HOST', _constants.DEFAULT_HOST),
        port=program.config.MOCKER_PORT or params.get('PORT', _constants.DEFAULT_PORT),
        debug=program.config.MOCKER_DEBUG or params.get('DEBUG'),
        gevent=program.config.GEVENT,
        path_to_mocks=program.config.MOCKER_PATH_TO_MOCKS or params.get('PATH_TO_MOCKS'),
        static_folder=program.config.MOCKER_STATIC_FOLDER or params.get(
            'STATIC_FOLDER', _constants.DEFAULT_STATIC_FOLDER,
        ),
        static_url_path=program.config.MOCKER_STATIC_URL_PATH or params.get(
            'STATIC_URL_PATH', _constants.DEFAULT_STATIC_URL_PATH,
        ),
        block_timeout=program.config.MOCKER_BLOCK_TIMEOUT or params.get(
            'BLOCK_TIMEOUT', _constants.DEFAULT_BLOCK_TIMEOUT,
        ),
    )

    program.shared_extension(
        _constants.EX_NAME, _Mocker, singleton=True, args=(config, ),
    )


__all__ = (
    'mock',
    'path',
    'unblock',
    'get_current_url',
    'get_current_static_url',
    'declare_external_resource',
)
