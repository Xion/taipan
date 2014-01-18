"""
Property utilities.
"""
from collections import defaultdict
import sys

from taipan.api.decorators import function_decorator
from taipan.functional import ensure_callable


__all__ = ['objectproperty', 'classproperty']


@function_decorator
class objectproperty(object):
    """Alternate version of the standard ``@property`` decorator,
    useful for properties exposing setter (or deleter) in addition to getter.

    It allows to contain all two/three functions and prevent PEP8 warnings
    about redefinion of ``x`` when using ``@x.setter`` or ``@x.deleter``.

    Usage::

        @objectproperty
        def foo():
            '''The foo property.'''
            def get(self):
                return self._foo
            def set(self, value):
                self._foo = value
            return locals()

    The ``return locals()`` statement at the end is optional
    but recommended for portability to more obscure Python implementations.
    """
    _ACCESSOR_NAMES = {
        'get': "getter",
        'set': "setter",
        'del': "deleter",
    }

    def __call__(self, func):
        """Construct property based on given function
        that has accessors (getter, setter and/or deleter) defined therein.
        """
        accessors = self._retrieve_accessors(func)
        kwargs = self._build_property_kwargs(accessors)
        return property(doc=func.__doc__, **kwargs)

    def _retrieve_accessors(self, func):
        """Call given function and retrieve the accesors
        which were defined there.

        Accessors shall be defined as locals within that function,
        optionally followed by returning them with ``return locals()``.
        """
        accessors = {}

        def trace_func(frame, event, arg):
            """Trace function for fetching locals defined within ``func``."""
            is_from_func = frame.f_code == func.__code__
            if event == 'return' and is_from_func:  # ``arg`` is return value
                accessors.update(arg or frame.f_locals)
            return trace_func

        # to obtain locals from ``func``, we set up a trace that intercepts
        # the exit of ``func``\ s scope and reads either its locals or
        # return value (so ``return locals()``, or similar, takes precedence)
        self._set_trace(trace_func)
        try:
            retval = func()
            if not accessors:  # fallback if ``sys.settrace`` didn't work
                if retval is None:
                    raise ValueError("`return locals()` is mandatory "
                                     "at the end of @objectproperty "
                                     "for this Python implementation")
                accessors.update(retval)
        finally:
            self._set_trace(None)

        return accessors

    def _build_property_kwargs(self, accessors):
        """Build dictionary of arguments to built-in :func:`property`
        based on given property accessors.
        """
        kwargs = defaultdict(list)

        # accomodate for various convenient naming conventions for accessors
        for name in ('get', 'set', 'del'):
            name_ = name + '_'
            fname = 'f' + name  # canonical @property argument name
            if name in accessors:
                kwargs[fname].append(accessors[name])
            if name_ in accessors:
                kwargs[fname].append(accessors[name_])

        # verify that we got at most one value for each type of accessor
        for name, functions in kwargs.items():
            if len(functions) > 1:
                raise ValueError("expected at most 1 %s; got %d instead" % (
                    self._ACCESSOR_NAMES[name], len(functions)))
            kwargs[name] = functions[0]

        return kwargs

    def _set_trace(self, trace_func):
        """Attempt to install a trace function.

        This is not guaranteed to do anything, although common
        Python implementations (CPython, PyPy) support tracing functions fine.
        """
        if hasattr(sys, 'settrace'):
            sys.settrace(trace_func)


class classproperty(object):
    """A read-only class property.

    Usage is exactly analogous to ``@property`` decorator.
    However, it's only possible to create a getter.
    """
    def __init__(self, getter):
        ensure_callable(getter)
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
