# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo_example',
    version='1.0',
    description='Wazo example plugin',
    author='Wazo Authors',
    author_email='dev@wazo.io',
    url='https://wazo.io',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wazo-example=wazo_example.main:main',
        ],
    },
)
