"""
Modifiers ("annotation" decorators) for classes and class members.
"""
import inspect

from taipan.objective import _get_first_arg_name
from taipan.objective.base import ObjectMetaclass
from taipan.objective.methods import ensure_method


__all__ = ['final', 'override']


def final(class_):
    """Mark a class as _final_, forbidding any more classes from
    inheriting from it (subclassing it).
    """
    if not inspect.isclass(class_):
        raise TypeError("@final can only be applied to classes")
    if not isinstance(class_, ObjectMetaclass):
        raise ValueError("@final can only be applied to subclasses of Object")

    class_.__final__ = True
    return class_


def override(method):
    """Mark a method as overriding a corresponding method from superclass.

    .. note::

        When overriding a :class:`classmethod`, remember to place ``@override``
        above the ``@classmethod`` decorator::

            class Foo(Bar):
                @override
                @classmethod
                def florb(cls):
                    pass
    """
    try:
        ensure_method(method)
    except TypeError:
        # in case user mixed up the order of ``@override`` and ``@classmethod``,
        # we can detect the issue and provide a targeted exception message
        if inspect.isfunction(method) and _get_first_arg_name(method) == 'cls':
            raise TypeError("@override must be applied above @classmethod")
        else:
            raise

    return _OverriddenMethod(method)


class _OverriddenMethod(object):
    """Wrapper for methods that have been marked with ``@override``.

    Those methods will be unpacked by :class:`ObjectMetaclass` during creation
    of the class which contains them.
    """
    def __init__(self, method):
        self.method = method

    # We proxy most operations to the underlying method to support the use case
    # when it's called / referenced / etc. even before its class is created.
    # An example would be a class attribute defined in terms of calling
    # an overridden class or static method.

    def __call__(self, *args, **kwargs):
        """Proxy calls to underlying method."""
        return self.method(*args, **kwargs)

    def __getattribute__(self, attr):
        """Proxy attribute access to underlying method."""
        if attr == 'method':
            return object.__getattribute__(self, attr)
        else:
            return getattr(self.method, attr)
