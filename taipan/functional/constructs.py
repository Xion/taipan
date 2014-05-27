"""
Functional constructs, emulating Python statements in expression form.
"""
import inspect
import sys

from taipan._compat import builtins
from taipan.api.fluency import fluent
from taipan.collections import (ensure_iterable, ensure_ordered_mapping,
                                is_mapping)
from taipan.functional import ensure_callable
from taipan.functional.functions import none


__all__ = [
    'pass_', 'print_', 'raise_', 'try_', 'with_',
    'Var', 'ValueAbsentError',
]


# Statements

__missing = object()


def pass_(*args, **kwargs):
    """Do nothing, swallowing any and all possible arguments
    that were passed to this function.

    This can be used in places where a function is otherwise required.
    """
    return pass_  # allows usage as both ``pass_`` and ``pass_()``


#: Alias for :func:`print`.
print_ = getattr(builtins, 'print')


def raise_(exception=__missing, *args, **kwargs):
    """Raise (or re-raises) an exception.

    :param exception: Exception object to raise, or an exception class.
                      In the latter case, remaining arguments are passed
                      to the exception's constructor.
                      If omitted, the currently handled exception is re-raised.
    """
    if exception is __missing:
        raise
    else:
        if inspect.isclass(exception):
            raise exception(*args, **kwargs)
        else:
            if args or kwargs:
                raise TypeError("can't pass arguments along with "
                                "exception object to raise_()")
            raise exception


def try_(block, except_=None, else_=None, finally_=None):
    """Emulate a ``try`` block.

    :param block: Function to be executed within the ``try`` statement
    :param except_: Function to execute when an :class:`Exception` occurs.
                    It receives a single argument: the exception object.
                    Alternatively, a list of key-value pairs can be passed,
                    mapping exception types to their handler functions.
    :param else_: Function to execute when ``block`` completes successfully.
                  Note that it requires ``except_`` to be provided as well
    :param finally_: Function to execute at the end,
                     regardless of whether an exception occurred or not

    :return:  If no exception was raised while executing ``block``,
              the result of ``else_`` (if provided) or ``block`` is returned.
              Otherwise, the result of ``except_`` is returned.

    Note that :func:`try_` can _still_ raise an exception if it occurs
    while evaluating ``except_``, ``else_`` or ``finally_`` functions.
    """
    ensure_callable(block)
    if not (except_ or else_ or finally_):
        raise TypeError("at least one of `except_`, `else_` or `finally_` "
                        "functions must be provided")
    if else_ and not except_:
        raise TypeError("`else_` can only be provided along with `except_`")

    if except_:
        if callable(except_):
            except_ = [(Exception, except_)]
        else:
            ensure_iterable(except_)
            if is_mapping(except_):
                ensure_ordered_mapping(except_)
                except_ = except_.items()

        def handle_exception():
            """Dispatch current exception to proper handler in ``except_``."""
            exc_type, exc_object = sys.exc_info()[:2]
            for t, handler in except_:
                if issubclass(exc_type, t):
                    return handler(exc_object)
            raise

        if else_:
            ensure_callable(else_)
            if finally_:
                ensure_callable(finally_)
                try:
                    block()
                except:
                    return handle_exception()
                else:
                    return else_()
                finally:
                    finally_()
            else:
                try:
                    block()
                except:
                    return handle_exception()
                else:
                    return else_()
        else:
            if finally_:
                ensure_callable(finally_)
                try:
                    return block()
                except:
                    return handle_exception()
                finally:
                    finally_()
            else:
                try:
                    return block()
                except:
                    return handle_exception()
    elif finally_:
        ensure_callable(finally_)
        try:
            return block()
        finally:
            finally_()


def with_(contextmanager, do):
    """Emulate a `with`` statement, performing an operation within context.

    :param contextmanager: Context manager to use for ``with`` statement
    :param do: Operation to perform: callable that receives the ``as`` value

    :return: Result of the operation

    Example::

        # read all lines from given list of ``files``
        all_lines = sum((with_(open(filename), do=dotcall('readlines'))
                         for filename in files), [])
    """
    # TODO(xion): extract an ``ensure_contextmanager`` function
    # once we figure out (or come up with) a correct place for it
    if not hasattr(contextmanager, '__exit__'):
        raise TypeError("%r is not a context manager" % (contextmanager,))
    ensure_callable(do)

    with contextmanager as value:
        return do(value)


# Variable object

@fluent
class Var(object):
    """Class representing a "variable" which can be assigned to
    (or initialized with) a value, to be retrieved at later time.

    The main application of :class:`Var` is including a mutable object
    inside a closure, so that the inner function can modify it.

    Here's rather superficial example::

        def count_parity(numbers):
            even_count = Var(0)
            odd_count = Var(0)

            def examine(number):
                if number % 2 == 0:
                    even_count.inc(1)
                else:
                    odd_count.inc(1)

            list(map(examine, numbers))
            return even_count.get(), odd_count.get()

    In real code, you'd use :class:`Var` to return a "result" from a function
    that is called in a special way, e.g. in a database transaction.

    .. note::

        As closures can be mutable in Python 3 (through ``nonlocal`` keyword),
        :class:`Var` is less useful there. (It can still be used to simulate
        assignments inside anonymous functions defined through ``lambda``).

    For further convenience, :class:`Var` objects also do behave as:

        * single-element iterables ("containing" the variable's value)
        * callables of arbitrary arity (returning the variable's value)
        * no-op context managers (think analogous to files opened by ``open``)
    """
    __slots__ = ['value', '__weakref__']

    ABSENT = object()

    def __init__(self, value=ABSENT):
        """Constructor.

        :param value: Initial value to store in the variable.
                      Can be omitted; if so, the variable will be "empty"
                      (uninitialized).
        """
        self.value = value

    def _ensure_has_value(self):
        if not self.has_value():
            raise ValueAbsentError()

    def clear(self):
        """Clears the vaiable, making it uninitialized."""
        self.value = self.ABSENT

    def dec(self, by=1):
        """Decrement the value stored in this variable.
        :param by: Optional amount to decrement the value by (default 1)
        :raise ValueAbsentError: When the variable has no value
        """
        self._ensure_has_value()
        self.value -= by

    @fluent.terminator
    def get(self):
        """Retrieves the value stored in this variable.
        :return: Variable's value if present
        :raise ValueAbsentError: When the variable has no value
        """
        self._ensure_has_value()
        return self.value

    @fluent.terminator
    def has_value(self):
        """Checks whether the variable has a value.
        :return: True if variable has a value, False otherwise
        """
        return self.value is not self.ABSENT

    def inc(self, by=1):
        """Increment the value stored in this variable.
        :param by: Optional amount to increment the value by (default 1)
        :raise ValueAbsentError: When the variable has no value
        """
        self._ensure_has_value()
        self.value += by

    def set(self, value):
        """Sets a new value of this variable.
        :param value: The value to set
        """
        self.value = value

    # Note that :class:`Var` intentionally doesn't have any magic methods
    # that would proxy to the underlying ``value``. For clarity,
    # all interactions with that value must be through named methods.

    def __call__(self, *args, **kwargs):
        return self.get()

    def __contains__(self, value):
        return self.has_value() and self.value is value

    def __enter__(self):
        return self

    __exit__ = none()

    def __iter__(self):
        return iter((self.value,) if self.has_value() else ())

    def __len__(self):
        return int(self.has_value())

    def __repr__(self):
        addr = hex(id(self))
        if self.has_value():
            return "<Var %r at %s>" % (self.value, addr)
        else:
            return "<Var at %s (empty)>" % addr

    __reversed__ = __iter__


class ValueAbsentError(TypeError):
    """Exception thrown when an operation on :class:`Var` is not possible
    because it doesn't have any value.
    """
    def __init__(self, msg=None):
        if msg is None:
            super(ValueAbsentError, self).__init__()
        else:
            super(ValueAbsentError, self).__init__(msg)
