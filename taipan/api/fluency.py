"""
Fluent API utilities.

"Fluent" or "chained" is style of writing state-changing methods of a class
that allows for chaining several calls to the same object together.

A common example is a query-like object in ORMs and similar libraries::

    results = (query(Model)
        .filter_by(some_field=42)
        .filter_by(other_field="foo")
        .group_by('third_field')
        .order_by('sort_order')
        .execute())

With the aid of this module, implementing such a mechanism is typically
as simple as adding a @\ :class:`fluent` decorator to the class.
"""
import functools

from taipan._compat import imap
from taipan.api.decorators import class_decorator
from taipan.collections import is_iterable
from taipan.functional import ensure_callable
from taipan.objective import is_internal, is_magic
from taipan.objective.methods import get_methods
from taipan.strings import ensure_string, is_string


__all__ = ['fluent', 'terminator', 'FluentError']


@class_decorator
class fluent(object):
    """Make the class' public methods use the "fluent" API style.

    To conform to the style, public methods of class decorated with
    @\ :class:`fluent` must not return any result (except possibly ``self``)
    to allow for chaning their calls.

    Possible exceptions include methods intended to end the chain, e.g.
    ``execute`` for query-like objects. These so-called *terminators*
    need to be explicitly marked by:

        * passing their names as ``terminators=`` argument
        * decorating them with @\ :func:`terminator`

    Here's an example of simplistic, fluent SQL query class::

        @fluent(terminators=['to_sql'])
        class Query(object):
            def __init__(self, table):
                self._table = table
                self._filters = {}

            def filter_by(self, **kwargs):
                self._filters.update(kwargs)

            def to_sql(self):
                query = "SELECT * FROM " + self._table
                if self._filters:
                    query += " WHERE " + " AND ".join(
                        "%s=%r" % f for f in self._filters.items())
                return query

    along with possible usage::

        >>> (Query('users')
                .filter_by(first_name="John")
                .filter_by(last_name="Smith"))
             .to_sql()
        "SELECT * FROM users WHERE first_name='John' AND last_name='Smith'"

    Notice how ``filter_by`` method does not require explicit ``return self``
    statement to permit chaining several invocations together.

    .. warning::

        The ``Query`` class is just an example and contains many fatal flaws,
        including the ripeness for SQL injection attacks.
        **Never** use something like this in your production code!
    """
    def __init__(self, **kwargs):
        self._terminators = self._get_terminators(kwargs)

    def __call__(self, class_):
        for name, method in get_methods(class_):
            if is_internal(name) or is_magic(name):
                continue

            # TODO(xion): warn about terminator method names
            # that haven't been encountered in the decorated ``class_``
            if not self._is_terminator(name, method):
                fluent_method = self._make_fluent(method)
                setattr(class_, name, fluent_method)

        return class_

    def _get_terminators(self, ctor_kwargs):
        """Retrieve fluent terminators from decorator's arguments."""
        terminators = []

        for terminator_arg in ('terminator', 'terminators'):
            if terminator_arg not in ctor_kwargs:
                continue
            terminator_arg_value = ctor_kwargs[terminator_arg]
            if is_string(terminator_arg_value):
                terminators.append(terminator_arg_value)
            elif is_iterable(terminator_arg_value):
                terminators.extend(imap(ensure_string, terminator_arg_value))
            else:
                raise TypeError(
                    "expected name or list of names of terminator methods; "
                    "got %r instead" % type(terminator_arg_value))

        return frozenset(terminators)

    def _is_terminator(self, name, method):
        return getattr(method, '__fluent_terminator', False) \
            or name in self._terminators

    def _make_fluent(self, method):
        """Wrap the method to include the fluent ``return self``."""
        @functools.wraps(method)
        def fluent_method(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            if result not in (None, self):
                raise FluentError(
                    "invalid @fluent return value: %r" % (result,))
            return self

        return fluent_method


def terminator(method):
    """Mark a public method of @\ :class:`fluent` class as *terminator*,
    i.e. a method that ends a chain of consecutive calls and returns a result.
    """
    ensure_callable(method)
    method.__fluent_terminator = True
    return method

#: Alias for @\ :func:`terminator`.
fluent.terminator = terminator


class FluentError(ValueError):
    """Error raised when @\ :class:`fluent` method returns unexpeced result."""
