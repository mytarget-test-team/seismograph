# -*- coding: utf-8 -*-

from .base import BaseMock
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

    def __install__(self, program):
        params = program.config.get(self.__config_key__, {})

        ex_kwargs = {
            'host': params.get('HOST'),
            'port': params.get('PORT'),
            'mocks': params.get('MOCKS'),
            'debug': params.get('DEBUG'),
            'mocks_path': params.get('MOCKS_PATH'),
            'server_type': params.get(
                'SERVER_TYPE', self.__default_server_type__,
            ),
            'gevent': program.config.GEVENT,
            'threading': program.config.THREADING,
            'multiprocessing': program.config.MULTIPROCESSING,
        }

        program.shared_extension(
            self.__ex_name__, self,
            kwargs=ex_kwargs,
            singleton=params.get('SINGLETON', False),
        )

    def __call__(self,
                 host=None,
                 port=None,
                 mocks=None,
                 debug=False,
                 gevent=False,
                 mocks_path=None,
                 threading=False,
                 multiprocessing=False,
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
            gevent=gevent,
            threading=threading,
            multiprocessing=multiprocessing,
        )


__all__ = (
    'BaseMock',
    'JsonMock',
    'SERVER_TYPES',
    'BaseMockServer',
    'JsonApiMockServer',
)
