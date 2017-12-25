# -*- coding: utf-8 -*-

import os
import sys
import shutil
from codecs import getwriter

from seismograph.utils import pyv


TMP_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(
            __file__,
        ),
        'tmp',
    ),
)

BIN_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(
            __file__,
        ),
        '..',
        'bin',
    ),
)


if os.path.exists(TMP_FOLDER):
    shutil.rmtree(TMP_FOLDER)
    os.mkdir(TMP_FOLDER)
else:
    os.mkdir(TMP_FOLDER)


MOCKER_EX = {
    'PORT': 5000,
    'DEBUG': False,
    'HOST': '127.0.0.1',
    'SERVER_TYPE': 'json_api',
    'PATH_TO_MOCKS': os.path.abspath(
        os.path.join(
            os.path.dirname(
                __file__,
            ),
            'mocks',
        ),
    ),
}


ALCHEMY_EX = {
    'PROTOCOL': 'mysql+mysqlconnector',
    'HOST': '127.0.0.1',
    'PORT': 3306,
    'USER': 'root',
    'DNS_PARAMS': {
        'charset': 'utf8',
        'use_unicode': 1,
    },
    'DATABASES': {
        'information_schema': {},
        'test': {
            'bind_key': 'test',
        },
    },
    'SESSION': {},
}


SELENIUM_EX = {
    'USE_REMOTE': False,
    'POLLING_TIMEOUT': 10,
    'POLLING_DELAY': None,
    'SCRIPT_TIMEOUT': None,
    'IMPLICITLY_WAIT': None,
    'WINDOW_SIZE': None,
    'MAXIMIZE_WINDOW': True,
    'DEFAULT_BROWSER': 'chrome',
    'PROJECT_URL': 'https://www.google.ru/',
    'SCREEN_PATH': TMP_FOLDER,
    'LOGS_PATH': TMP_FOLDER,

    'IE': {},
    'OPERA': {},
    'FIREFOX': {},
    'PHANTOMJS': {
        'executable_path': os.path.join(BIN_FOLDER, 'phantomjs'),
        'service_log_path': os.path.join(TMP_FOLDER, 'phantomjs.log'),
    },
    'CHROME': {
        'executable_path': os.path.join(BIN_FOLDER, 'chromedriver'),
        # 'service_log_path': os.path.join(TMP_FOLDER, 'chromedriver.log'),
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
            'format': '%(asctime)-15s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'basic'
        },
        'null': {
            'class': 'logging.NullHandler',
            'level': 'DEBUG'
        },
    },
    'loggers': {
        'steps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'seismograph': {
            'propagate': False,
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

if pyv.IS_PYTHON_2:
    LOGGING_SETTINGS['handlers']['console']['stream'] = getwriter('utf-8')(sys.stderr)
