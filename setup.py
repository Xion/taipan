#!/usr/bin/env python
"""
taipan
======

General purpose toolkit for Python
"""
import ast
import os
from setuptools import find_packages, setup
import sys


PACKAGE = 'taipan'


def read_tag(name):
    """Reads the value of a "magic tag" defined in the main __init__.py file
    of the package.

    :param name: Tag name, without the leading and trailing underscores
    :return: Tag's value or None
    """
    filename = os.path.join(PACKAGE, '__init__.py')
    with open(filename) as f:
        ast_tree = ast.parse(f.read(), filename)

    for node in ast.walk(ast_tree):
        if type(node) is not ast.Assign:
            continue

        target = node.targets[0]
        if type(target) is not ast.Name:
            continue

        if not (target.id.startswith('__') and target.id.endswith('__')):
            continue

        target_name = target.id[2:-2]
        if target_name == name:
            return ast.literal_eval(node.value)


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
    name=PACKAGE,
    version=read_tag('version'),
    description="General purpose toolkit for Python",
    long_description=__doc__,  # TODO(xion): add README.rst
    author=read_tag('author'),
    url="http://github.com/Xion/taipan",
    license=read_tag('license'),

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
