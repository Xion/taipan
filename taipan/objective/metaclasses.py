"""
Metaclass related functions and utilities.
"""

# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.

import inspect

from taipan.api.decorators import _wrap_decorator
from taipan.functional.combinators import and_, not_


__all__ = [
    'is_metaclass', 'ensure_metaclass',
    'metaclass',
]


def is_metaclass(obj):
    """Checks whether given object is a metaclass.
    :return: ``True`` if object is a metaclass, ``False`` otherwise
    """
    return issubclass(obj, type)


def ensure_metaclass(arg):
    """Check whether argument is a metaclass.
    :return: Argument, if it's a metaclass
    :raise TypeError: When argument is not a metaclass
    """
    if not is_metaclass(arg):
        raise TypeError(
            "expected a metaclass, got %s instead" % type(arg).__name__)
    return arg


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
        self.metaclass = ensure_metaclass(meta)

    def __call__(self, cls):
        """Apply the decorator to given class.

        This recreates the class using the previously supplied metaclass.
        """
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

# The decorator can be applied to classes that aren't themselves metaclasses.
metaclass = _wrap_decorator(MetaclassDecorator, "non-meta classes",
                            and_(inspect.isclass, not_(is_metaclass)))
metaclass.__name__ = 'metaclass'
del MetaclassDecorator
