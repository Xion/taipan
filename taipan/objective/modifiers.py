"""
Modifiers ("annotation" decorators) for classes and class members.
"""
import inspect

from taipan._compat import IS_PY26
from taipan.objective import _get_first_arg_name
from taipan.objective.base import ObjectMetaclass
from taipan.objective.methods import ensure_method, NonInstanceMethod


__all__ = ['final', 'override']


def final(class_):
    """Mark a class as _final_, forbidding any more class from
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

    # non-instance methods do not allow setting attributes on them,
    # so we mark the underlying raw functions instead
    if isinstance(method, NonInstanceMethod):
        # TODO(xion): support @override on non-instance methods in Python 2.6
        # by returning a special wrapper object around them, which would be
        # subsequently unwrapped by ObjectMetaclass.__new__
        if IS_PY26:
            raise NotImplementedError("@override on non-instance methods "
                                      "is not supported in Python 2.6")
        method.__func__.__override__ = True
    else:
        method.__override__ = True

    return method
