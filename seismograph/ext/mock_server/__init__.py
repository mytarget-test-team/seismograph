# -*- coding: utf-8 -*-

from optparse import OptionGroup

from .mock import BaseMock
from .base import BaseMockServer
from .json_api_mock import JsonMock
from .json_api_mock import JsonApiMockServer

from ...extensions import BaseExtension
from ...exceptions import EmergencyStop


SERVER_TYPES = {
    'simple': BaseMockServer,
    'json_api': JsonApiMockServer,
}


class MockServerExtension(BaseExtension):

    __ex_name__ = 'mock_server'
    __config_key__ = 'MOCK_SERVER_EX'
    __default_server_type__ = 'json_api'

    @staticmethod
    def __add_options__(parser):
        group = OptionGroup(parser, 'MockServer extension options')

        group.add_option(
            '--mock-server-mocks-dir',
            dest='MOCK_SERVER_MOCKS_DIR',
            default=None,
        )
        group.add_option(
            '--mock-server-host',
            dest='MOCK_SERVER_HOST',
            default=None,
        )
        group.add_option(
            '--mock-server-port',
            dest='MOCK_SERVER_PORT',
            default=None,
            type=int,
        )
        group.add_option(
            '--mock-server-debug',
            dest='MOCK_SERVER_DEBUG',
            action='store_true',
            default=False,
        )

        parser.add_option_group(group)

    def __install__(self, program):
        params = program.config.get(self.__config_key__, {})

        ex_kwargs = {
            'mocks': params.get('MOCKS'),
            'host': program.config.MOCK_SERVER_HOST or params.get('HOST'),
            'port': program.config.MOCK_SERVER_PORT or params.get('PORT'),
            'debug': program.config.MOCK_SERVER_DEBUG or params.get('DEBUG'),
            'mocks_path': program.config.MOCK_SERVER_MOCKS_DIR or params.get('MOCKS_PATH'),
            'server_type': params.get(
                'SERVER_TYPE', self.__default_server_type__,
            ),
        }

        program.shared_extension(
            self.__ex_name__, self, singleton=True, kwargs=ex_kwargs,
        )

    def __call__(self,
                 host=None,
                 port=None,
                 mocks=None,
                 debug=False,
                 mocks_path=None,
                 server_type=__default_server_type__):
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
        )


__all__ = (
    'BaseMock',
    'JsonMock',
    'SERVER_TYPES',
    'BaseMockServer',
    'JsonApiMockServer',
)
