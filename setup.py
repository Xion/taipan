#!/usr/bin/env python
"""
taipan
======

General purpose toolkit for Python
"""
from setuptools import find_packages, setup

import taipan


setup(
    name="taipan",
    version=taipan.__version__,
    description="General purpose toolkit for Python",
    long_description=__doc__,  # TODO(xion): add README.rst
    author=taipan.__author__,
    url="http://github.com/Xion/taipan",
    license=taipan.__license__,

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    platforms='any',
    packages=find_packages(exclude=['tests']),

    tests_require=open('requirements-test.txt').readlines(),
)
