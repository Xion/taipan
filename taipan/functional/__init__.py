"""
Functional programming utilities.
"""
from taipan.collections import ensure_iterable, ensure_mapping, ensure_sequence
from taipan.strings import ensure_string


def ensure_callable(arg):
    """Checks whether given object is a callable.
    :return: Argument if it's a callable
    :raise TypeError: When argument is not a callable
    """
    if not callable(arg):
        raise TypeError("expected a callable, got %s" % type(arg).__name__)
    return arg


def ensure_argcount(args, min_=None, max_=None):
    """Checks whether iterable of positional arguments satisfies conditions.

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


def ensure_keyword_args(kwargs, mandatory=(), optional=()):
    """Checks whether dictionary of keyword arguments satisfies conditions.

    :param kwargs: Dictionary of keyword arguments, received via ``*kwargs``
    :param mandatory: Iterable of mandatory argument names
    :param optional: Iterable of optional argument names

    :return: ``kwargs`` if the conditions are met:
             all ``mandatory`` arguments are present, and besides that
             no arguments outside of ``optional`` ones are.

    :raise TypeError: When conditions are not met
    """
    ensure_mapping(kwargs)
    mandatory = list(map(ensure_string, ensure_iterable(mandatory)))
    optional = list(map(ensure_string, ensure_iterable(optional)))
    if not (mandatory or optional):
        raise ValueError(
            "mandatory and/or optional argument names must be provided")

    names = set(kwargs)
    for name in mandatory:
        try:
            names.remove(name)
        except KeyError:
            raise TypeError(
                "no value for mandatory keyword argument '%s'" % name)

    excess = names - set(optional)
    if excess:
        if len(excess) == 1:
            raise TypeError("unexpected keyword argument '%s'" % excess.pop())
        else:
            raise TypeError("unexpected keyword arguments: %s" % tuple(excess))

    return kwargs
