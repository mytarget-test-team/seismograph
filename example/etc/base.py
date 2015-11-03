# -*- coding: utf-8 -*-

import os


MOCK_SERVER_EX = {
    'HOST': '127.0.0.1',
    'PORT': 5000,
    'DEBUG': False,
    'SERVER_TYPE': 'json_api',
    'MOCKS_PATH': os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__,
            ),
            'mocks',
        ),
    ),
    'SINGLETON': False,
}
