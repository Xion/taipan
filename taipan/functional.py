"""
Functional utilities.
"""


def ensure_callable(arg):
    """Checks whether given object is a callable.
    :return: Argument if it's a callable
    :raises TypeError: When argument is not a callable
    """
    if not callable(arg):
        raise TypeError("expected a callable, got %s" % type(arg).__name__)
    return arg
