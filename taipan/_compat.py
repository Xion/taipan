"""
Compatibility shims for different Python versions.
"""
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import django.utils.simplejson as json


import sys
IS_PY3 = sys.version[0] == '3'
IS_PY25 = sys.version[0] == '2' and int(sys.version[2]) <= 5


if IS_PY3:
    imap = map
    unichr = chr
    xrange = range
else:
    from itertools import imap


if IS_PY25:
    import __builtin__
    __builtin__.bytes = bytes = str
