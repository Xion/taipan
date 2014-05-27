"""
Method related functions and utilities.
"""
import inspect

from taipan.objective import _get_first_arg_name


__all__ = [
    'NonInstanceMethod',
    'is_method', 'ensure_method',
    'get_methods',
]


#: Tuple of non-instance method types (class method & static method).
NonInstanceMethod = (classmethod, staticmethod)


def is_method(arg):
    """Checks whether given object is a method."""
    if inspect.ismethod(arg):
        return True
    if isinstance(arg, NonInstanceMethod):
        return True

    # Unfortunately, there is no disctinction between instance methods
    # that are yet to become part of a class, and regular functions.
    # We attempt to evade this little gray zone by relying on extremely strong
    # convention (which is nevertheless _not_ enforced by the intepreter)
    # that first argument of an instance method must be always named ``self``.
    if inspect.isfunction(arg):
        return _get_first_arg_name(arg) == 'self'

    return False


def ensure_method(arg):
    """Checks whether given object is a class or instance method
    :return: Argument if it's a method
    :raise TypeError: When argument is not a method
    """
    if not is_method(arg):
        raise TypeError("expected a method, got %s" % type(arg).__name__)
    return arg


def get_methods(class_):
    """Retrieve all methods of a class."""
    return inspect.getmembers(class_, is_method)
