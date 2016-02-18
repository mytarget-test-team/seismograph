# -*- coding: utf-8 -*-

from optparse import OptionGroup

from .mock import BaseMock
from .base import BaseMockServer
from .json_api_mock import JsonMock
from .json_api_mock import JsonApiMockServer

from ...exceptions import EmergencyStop


EX_NAME = 'mocker'
CONFIG_KEY = 'MOCKER_EX'
DEFAULT_SERVER_TYPE = 'json_api'

SERVER_TYPES = {
    'simple': BaseMockServer,
    'json_api': JsonApiMockServer,
}


def create_server(host=None,
                  port=None,
                  mocks=None,
                  debug=False,
                  mocks_path=None,
                  server_type=DEFAULT_SERVER_TYPE,
                  **kwargs):
    try:
        mock_server_class = SERVER_TYPES[server_type]
    except KeyError:
        raise EmergencyStop(
            'Incorrect server type "{}"'.format(server_type),
        )

    return mock_server_class(
        mocks_path,
        host=host,
        port=port,
        mocks=mocks,
        debug=debug,
        **kwargs
    )


def __add_options__(parser):
    group = OptionGroup(parser, 'MockServer extension options')

    group.add_option(
        '--mock-server-mocks-dir',
        dest='MOCK_SERVER_MOCKS_DIR',
        default=None,
        help='Path to dir within mock files.'
    )
    group.add_option(
        '--mock-server-host',
        dest='MOCK_SERVER_HOST',
        default=None,
        help='Server host.',
    )
    group.add_option(
        '--mock-server-port',
        dest='MOCK_SERVER_PORT',
        default=None,
        type=int,
        help='Server port.',
    )
    group.add_option(
        '--mock-server-debug',
        dest='MOCK_SERVER_DEBUG',
        action='store_true',
        default=False,
        help='Use debug.',
    )

    parser.add_option_group(group)


def __install__(program):
    params = program.config.get(CONFIG_KEY, {})

    ex_kwargs = {
        'mocks': params.get('MOCKS'),
        'host': program.config.MOCK_SERVER_HOST or params.get('HOST'),
        'port': program.config.MOCK_SERVER_PORT or params.get('PORT'),
        'debug': program.config.MOCK_SERVER_DEBUG or params.get('DEBUG'),
        'mocks_path': program.config.MOCK_SERVER_MOCKS_DIR or params.get('MOCKS_PATH'),
        'server_type': params.get(
            'SERVER_TYPE', DEFAULT_SERVER_TYPE,
        ),
        'multiprocessing': program.config.MULTIPROCESSING,
        'threading': program.config.THREADING,
        'gevent': program.config.GEVENT,
    }

    program.shared_extension(
        EX_NAME, create_server, singleton=True, kwargs=ex_kwargs,
    )


__all__ = (
    'BaseMock',
    'JsonMock',
    'SERVER_TYPES',
    'BaseMockServer',
    'JsonApiMockServer',
)
