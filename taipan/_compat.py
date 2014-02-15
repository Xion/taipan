"""
Compatibility shims for different Python versions and platforms.
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

import platform
IS_PYPY = platform.python_implementation() == 'PyPy'


unichr = chr if IS_PY3 else unichr
xrange = range if IS_PY3 else xrange

if IS_PY3:
    ifilter = filter
    imap = map
    izip = zip
    from itertools import (
        zip_longest as izip_longest,
        filterfalse as ifilterfalse,
    )
else:
    from itertools import ifilter, ifilterfalse, imap, izip, izip_longest
