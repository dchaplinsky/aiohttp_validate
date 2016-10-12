#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'aiohttp==1.0.5',
    'jsonschema==2.5.1',
]

test_requirements = [
    'pytest==2.9.2',
    'pytest-aiohttp==0.1.3',
]

setup(
    name='aiohttp_validate',
    version='0.1.1',
    description="Simple library that helps you validate your API endpoints requests/responses with json schema",
    long_description=readme + '\n\n' + history,
    author="Dmitry Chaplinsky",
    author_email='chaplinsky.dmitry@gmail.com',
    url='https://github.com/dchaplinsky/aiohttp_validate',
    packages=[
        'aiohttp_validate',
    ],
    package_dir={'aiohttp_validate':
                 'aiohttp_validate'},
    entry_points={
        'console_scripts': [
            'aiohttp_validate=aiohttp_validate.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='aiohttp_validate',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
