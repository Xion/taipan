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
IS_PY3 = sys.version_info[0] == 3


unichr = chr if IS_PY3 else unichr
xrange = range if IS_PY3 else xrange

if IS_PY3:
    ifilter = filter
    imap = map
else:
    from itertools import ifilter, imap


Numeric = (int,) if IS_PY3 else (int, long)
