# coding=utf-8
import sys

from setuptools import find_packages
from setuptools import setup

assert sys.version_info[0] == 3 and sys.version_info[1] >= 6, "hive requires Python 3.6 or newer"

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-pylint',
    'pytest-asyncio',
    'pytest-console-scripts',
    'git-pylint-commit-hook',
    'pep8',
    'yapf',
]

# yapf: disable
setup(
    name='hivemind',
    version_format='0.0.1+{gitsha}',
    description='Developer-friendly microservice powering social networks on the Steem blockchain.',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['scripts']),
    setup_requires=['pytest-runner', 'setuptools-git-version'],
    tests_require=tests_require,
    dependency_links=[
      'https://github.com/bcb/jsonrpcserver/tarball/8f3437a19b6d1a8f600ee2c9b112116c85f17827#egg=jsonrpcserver-4.1.3+8f3437a'
    ],
    install_requires=[
        #'aiopg==0.16.0',
        'aiopg @ https://github.com/aio-libs/aiopg/tarball/862fff97e4ae465333451a4af2a838bfaa3dd0bc',
        'jsonrpcserver @ https://github.com/bcb/jsonrpcserver/tarball/8f3437a19b6d1a8f600ee2c9b112116c85f17827#egg=jsonrpcserver',
        'simplejson',
        'aiohttp',
        'certifi',
        'sqlalchemy',
        'funcy',
        'toolz',
        'maya',
        'ujson',
        'urllib3',
        'psycopg2-binary',
        'aiocache',
        'configargparse',
        'pdoc',
        'diff-match-patch'
    ],
    extras_require={'test': tests_require},
    entry_points={
        'console_scripts': [
            'hive=hive.cli:run',
        ]
    })
