# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


__version__ = '0.0.1'


if __name__ == '__main__':
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
        install_requires=[
            'six',
            'requests',
            'flask>=0.7',
        ],
        entry_points={
            'console_scripts': [
                'seismograph = seismograph.__main__:main',
            ],
        },
        test_suite='tests',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Testing',
        ],
    )
