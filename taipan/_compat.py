"""
Compatibility shims for different Python versions and platforms.
"""
import sys
IS_PY26 = sys.version_info[:2] == (2, 6)
IS_PY3 = sys.version_info[0] == 3


# Modules

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import django.utils.simplejson as json


# Global symbols

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


# Other

class MetaclassDecorator(object):
    """Decorator for creating a class through a metaclass.

    Unlike ``__metaclass__`` attribute from Python 2, or ``metaclass=`` keyword
    argument from Python 3, the ``@metaclass`` decorator works with both
    versions of the language.

    Example::

        @metaclass(MyMetaclass)
        class MyClass(object):
            pass
    """
    def __init__(self, meta):
        if not issubclass(meta, type):
            raise TypeError(
                "expected a metaclass, got %s instead" % type(meta).__name__)
        self.metaclass = meta

    def __call__(self, cls):
        """Apply the decorator to given class.

        This recreates the class using the previously supplied metaclass.
        """
        # Copyright (c) Django Software Foundation and individual contributors.
        # All rights reserved.

        original_dict = cls.__dict__.copy()
        original_dict.pop('__dict__', None)
        original_dict.pop('__weakref__', None)

        slots = original_dict.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slot in slots:
                original_dict.pop(slot)

        return self.metaclass(cls.__name__, cls.__bases__, original_dict)

metaclass = MetaclassDecorator
del MetaclassDecorator
