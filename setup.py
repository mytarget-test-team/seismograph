# -*- coding: utf-8 -*-

"""
Environments:

SIMPLE_SEISMOGRAPH - to install library without requirements of extensions
SEISMOGRAPH_EXTENSIONS - names of extensions separated by commas
"""

import os

from setuptools import setup
from setuptools import find_packages


__version__ = '0.1.3'


REQUIREMENTS = [
    'six>=1.4',
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

SIMPLE_INSTALL = os.getenv('SIMPLE_SEISMOGRAPH')
EXTENSIONS_TO_INSTALL = os.getenv('SEISMOGRAPH_EXTENSIONS', '')


def get_requirements():
    requirements = []
    requirements.extend(REQUIREMENTS)

    if SIMPLE_INSTALL:
        return requirements

    extensions_to_install = [
        n.strip()
        for n in EXTENSIONS_TO_INSTALL.split(',')
        if n.strip()
    ]

    if extensions_to_install:
        for ex_name in extensions_to_install:
            try:
                requirements.extend(
                    EX_REQUIREMENTS[ex_name],
                )
            except KeyError:
                raise RuntimeError('Unknown extension name: {}'.format(ex_name))
    else:
        for ex_name in EX_REQUIREMENTS:
            requirements.extend(EX_REQUIREMENTS[ex_name])

    return requirements


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
        install_requires=get_requirements(),
        entry_points={
            'console_scripts': (
                'seismograph = seismograph.__main__:main',
                'seismograph.mocker = seismograph.ext.mocker.__main__:main',
            ),
        },
        test_suite='tests',
        classifiers=(
            'Development Status :: 3 - Alpha',
            'Framework :: Seismograph',
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
    install_package()
