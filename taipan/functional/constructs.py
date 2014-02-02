"""
Functional constructs, emulating Python statements in expression form.
"""
from __future__ import print_function

import inspect
import sys

from taipan.functional import ensure_callable


__all__ = ['pass_', 'print_', 'raise_', 'try_', 'with_']


__missing = object()


def pass_(*args, **kwargs):
    """Do nothing, swallowing any and all possible arguments
    that were passed to this function.

    This can be used in places where a function is otherwise required.
    """
    return pass_  # allows usage as both ``pass_`` and ``pass_()``


#: Alias for :func:`print`.
print_ = print


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
    :param except_: Function to execute when an exception occurs.
                    It receives a single argument: the exception object
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
        ensure_callable(except_)
        if else_:
            ensure_callable(else_)
            if finally_:
                ensure_callable(finally_)
                try:
                    block()
                except:
                    return except_(sys.exc_info()[1])
                else:
                    return else_()
                finally:
                    finally_()
            else:
                try:
                    block()
                except:
                    return except_(sys.exc_info()[1])
                else:
                    return else_()
        else:
            if finally_:
                ensure_callable(finally_)
                try:
                    return block()
                except:
                    _, e, _ = sys.exc_info()
                    return except_(e)
                finally:
                    finally_()
            else:
                try:
                    return block()
                except:
                    return except_(sys.exc_info()[1])
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
    if not hasattr(contextmanager, '__exit__'):
        raise TypeError("%r is not a context manager" % (contextmanager,))
    ensure_callable(do)

    with contextmanager as value:
        return do(value)
