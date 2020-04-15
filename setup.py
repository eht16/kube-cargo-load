# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from os import path
from setuptools import setup
from shutil import rmtree
import sys

NAME = 'kube-cargo-load'
VERSION = '1.1'

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), 'rb') as f:
    LONG_DESCRIPTION = f.read().decode('utf-8')


if 'bdist_wheel' in sys.argv:
    # Remove previous build dir when creating a wheel build, since if files have been removed
    # from the project, they'll still be cached in the build dir and end up as part of the
    # build, which is really neat!
    for directory in ('build', 'dist', 'kube_cargo_load.egg-info'):
        rmtree(directory, ignore_errors=True)


setup(
    name=NAME,
    py_modules=['kubecargoload'],
    version=VERSION,
    description='Kubernetes POD memory limits and usage overview.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license='Apache License 2.0',
    author='Enrico Tröger',
    author_email='enrico.troeger@uvena.de',
    url='https://github.com/eht16/kube-cargo-load',
    project_urls={
        'Source code': 'https://github.com/eht16/kube-cargo-load/',
    },
    entry_points={
        'console_scripts': ['kubecargoload=kubecargoload:main']
    },
    keywords='kubernetes pod memory usage',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
