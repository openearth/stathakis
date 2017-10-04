#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(SiggyF): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'requests'
    # TODO: put package test requirements here
]

setup(
    name='stathakis',
    version='0.1.0',
    description="Measurement proxy. Consistent api for different sources of measurements. ",
    long_description=readme + '\n\n' + history,
    author="Fedor Baart",
    author_email='fedor.baart@deltares.nl',
    url='https://github.com/SiggyF/stathakis',
    packages=find_packages(include=['stathakis']),
    entry_points={
        'console_scripts': [
            'stathakis=stathakis.cli:main'
        ]
    },
    scripts=[
        'scripts/mount_efs'
    ],
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='stathakis',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
