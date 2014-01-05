#!/usr/bin/env python
"""
taipan
======

General purpose toolkit for Python
"""
from setuptools import find_packages, setup
import os
import sys

import taipan


def read_requirements(filename='requirements.txt'):
    """Reads the list of requirements from given file.

    :param filename: Filename to read the requirements from.
                     Uses ``'requirements.txt'`` by default.

    :return: Requirments as list of strings.
    """
    # allow for some leeway with the argument
    if not filename.startswith('requirements'):
        filename = 'requirements-' + filename
    if not os.path.splitext(filename)[1]:
        filename += '.txt'  # no extension, add default

    def valid_line(line):
        line = line.strip()
        return line and not any(line.startswith(p) for p in ('#', '-'))

    def extract_requirement(line):
        egg_eq = '#egg='
        if egg_eq in line:
            _, requirement = line.split(egg_eq, 1)
            return requirement
        return line

    with open(filename) as f:
        lines = f.readlines()
        return list(map(extract_requirement, filter(valid_line, lines)))


def get_test_requirements():
    """Get the list of test requirements
    for ``tests_require`` parameter of ``setup()``.
    """
    requirements = read_requirements('test')
    if sys.version_info <= (2, 7):
        requirements.extend(read_requirements('test-py26'))
    return requirements


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

    tests_require=get_test_requirements(),
)
