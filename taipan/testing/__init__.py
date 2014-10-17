"""
Functions and classes related to testing.

This package is inteded to replace the standard :module:`unittest`.
Test code should import all required :module:`unittest` symbols from here::

    from taipan.testing import skipIf, TestCase  # etc.
"""
from taipan.testing._unittest import *
from taipan.testing.skips import *
from taipan.testing.testcase import TestCase
