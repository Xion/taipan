"""
Compatibility module to ensure :module:`unittest2` symbols are available.
"""
try:
    from unittest2 import *
except ImportError:
    from unittest import *
