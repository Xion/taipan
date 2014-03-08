"""
Object-oriented programming utilities.
"""
import inspect

from taipan.strings import is_string


__all__ = ['is_internal', 'is_magic']


def is_internal(member):
    """Checks whether given class/instance member, or its name, is internal."""
    name = _get_member_name(member)
    return name.startswith('_') and not is_magic(name)


def is_magic(member):
    """Checks whether given class/instance member, or its name, is "magic".

    Magic fields and methods have names that begin and end
    with double underscores, such ``__hash__`` or ``__eq__``.
    """
    name = _get_member_name(member)
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


# Utility functions

def _get_member_name(member):
    if is_string(member):
        return member

    # Python has no "field declaration" objects, so the only valid
    # class or instance member is actually a method
    from taipan.objective.methods import ensure_method
    ensure_method(member)
    return member.__name__


def _get_first_arg_name(function):
    argnames, _, _, _ = inspect.getargspec(function)
    return argnames[0] if argnames else None
