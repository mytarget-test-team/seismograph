# -*- coding: utf-8 -*-

"""
Environments:

SIMPLE_SEISMOGRAPH - to install library without requirements of extensions
SEISMOGRAPH_EXTENSIONS - names of extensions separated by commas
"""

import os
import re

from setuptools import setup
from setuptools import find_packages


with open('seismograph/__init__.py') as _:
    __version__ = re.search(r"__version__\s*=\s*'(.*)'", _.read(), re.M).group(1)
assert __version__


EXTENSIONS = [
    'mocker',
    'alchemy',
    'selenium',
]

REQUIREMENTS = [
    'six>=1.4',
]

CONSOLE_SCRIPTS = [
    'seismograph = seismograph.__main__:main',
]

EX_REQUIREMENTS = {
    'mocker': [
        'requests',
        'flask>=0.7',
    ],
    'selenium': [
        'selenium>=2.46',
    ],
    'alchemy': [
        'sqlalchemy>=0.8',
    ],
}

EX_CONSOLE_SCRIPTS = {
    'mocker': [
        'seismograph.mocker = seismograph.ext.mocker.__main__:main',
    ],
}

SIMPLE_INSTALL = os.getenv('SIMPLE_SEISMOGRAPH')
EXTENSIONS_TO_INSTALL = os.getenv('SEISMOGRAPH_EXTENSIONS')


def prepare_extension_data(ex_name):
    if ex_name not in EXTENSIONS:
        raise RuntimeError(
            'Unknown extension name: {}'.format(ex_name),
        )

    requirements = EX_REQUIREMENTS.get(ex_name)
    console_scripts = EX_CONSOLE_SCRIPTS.get(ex_name)

    if requirements:
        REQUIREMENTS.extend(requirements)

    if console_scripts:
        CONSOLE_SCRIPTS.extend(console_scripts)


def prepare_data():
    if SIMPLE_INSTALL:
        return

    if EXTENSIONS_TO_INSTALL:
        extensions_to_install = [
            n.strip()
            for n in EXTENSIONS_TO_INSTALL.split(',')
            if n.strip()
        ]
        for ex_name in extensions_to_install:
            prepare_extension_data(ex_name)
    else:
        for ex_name in EXTENSIONS:
            prepare_extension_data(ex_name)


def install_package():
    setup(
        name='seismograph',
        version=__version__,
        url='https://github.com/trifonovmixail/seismograph',
        packages=find_packages(exclude=('example*', 'tests*')),
        author='Mikhail Trifonov',
        author_email='trifonovmixail@ya.ru',
        license='GNU LGPL',
        description='Framework for test development',
        keywords='test unittest framework',
        long_description=open('README.rst').read(),
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=REQUIREMENTS,
        entry_points={
            'console_scripts': CONSOLE_SCRIPTS,
        },
        test_suite='tests',
        classifiers=(
            'Development Status :: 4 - Beta',
            'Natural Language :: Russian',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Software Development :: Testing',
        ),
    )


if __name__ == '__main__':
    prepare_data()
    install_package()
