# -*- coding: utf-8 -*-

import os
import sys
from codecs import getwriter


MOCK_SERVER_EX = {
    'PORT': 5000,
    'DEBUG': False,
    'HOST': '127.0.0.1',
    'SERVER_TYPE': 'json_api',
    'MOCKS_PATH': os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__,
            ),
            'mocks',
        ),
    ),
}


SELENIUM_EX = {
    'USE_REMOTE': False,
    'POLLING_TIMEOUT': 10,
    'MAXIMIZE_WINDOW': True,
    'DEFAULT_BROWSER': 'chrome',
    'PROJECT_URL': 'http://google.com',
    'SCREEN_PATH': os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__,
            ),
            'tmp',
        ),
    ),
    'CHROME': {
        'executable_path': os.path.join(
            os.path.dirname(
                __file__,
            ),
            '..',
            'bin',
            'chromedriver',
        ),
    },
    'REMOTE': {
        'CAPABILITIES': {
            'chrome': {
                'version': '41',
            },
        },
        'OPTIONS': {
            'keep_alive': True,
            'command_executor': 'http://localhost:4444/wd/hub',
        },
    },
}


LOGGING_SETTINGS = {
    'version': 1,
    'formatters': {
        'basic': {
            'format': '%(asctime)-15s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': getwriter('utf-8')(sys.stderr),
            'formatter': 'basic'
        },
        'null': {
            'class': 'logging.NullHandler',
            'level': 'DEBUG'
        },
    },
    'loggers': {
        'example': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'propagate': False,
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
