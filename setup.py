#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for confluence.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup, find_packages

# try:
#     require('setuptools>=38.3')
# except VersionConflict:
#     print("Error: version of setuptools is too old (<38.3)!")
#     sys.exit(1)

setup(
    name = 'confluence',
    version = '0.0.1',
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'confluence = src.confluence.confluence:main',
            'confluence-merge = src.confluence.merge.main'
        ],
    },
)

# if __name__ == "__main__":
#     setup(use_pyscaffold=True)
