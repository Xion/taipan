"""
Functional programming utilities.
"""
from taipan.collections import ensure_sequence


def ensure_callable(arg):
    """Checks whether given object is a callable.
    :return: Argument if it's a callable
    :raise TypeError: When argument is not a callable
    """
    if not callable(arg):
        raise TypeError("expected a callable, got %s" % type(arg).__name__)
    return arg


def ensure_argcount(args, min_=None, max_=None):
    """Checks whether iterable of positional arguments satisfies condictions.

    :param args: Iterable of positional arguments, received via ``*args``
    :param min_: Minimum number of arguments
    :param max_: Maximum number of arguments

    :return: ``args`` if the conditions are met
    :raise TypeError: When conditions are not met
    """
    ensure_sequence(args)

    has_min = min_ is not None
    has_max = max_ is not None
    if not (has_min or has_max):
        raise ValueError(
            "minimum and/or maximum number of arguments must be provided")
    if has_min and has_max and min_ > max_:
        raise ValueError(
            "maximum number of arguments must be greater or equal to minimum")

    if has_min and len(args) < min_:
        raise TypeError(
            "expected at least %s arguments, got %s" % (min_, len(args)))
    if has_max and len(args) > max_:
        raise TypeError(
            "expected at most %s arguments, got %s" % (max_, len(args)))

    return args


from .combinators import *
from .constructs import *
from .functions import *
