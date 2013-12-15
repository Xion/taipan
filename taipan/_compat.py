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


if IS_PY3:
    imap = map
    unichr = chr
    xrange = range
else:
    from itertools import imap
