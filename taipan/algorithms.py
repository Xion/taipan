"""
General purpose algorithms dealing with data structures.
"""
from __future__ import absolute_import

from collections import deque
from itertools import chain, cycle as cycle_, islice, repeat
from numbers import Integral

from taipan._compat import imap, izip_longest
from taipan.collections import ensure_countable, ensure_iterable
from taipan.functional import ensure_callable
from taipan.functional.functions import identity


__all__ = [
    'batch', 'cycle', 'intertwine', 'iterate', 'pad', 'unique',
    'breadth_first', 'depth_first',
]


# Itertools recipes

def batch(iterable, n, fillvalue=None):
    """Batches the elements of given iterable.

    Resulting iterable will yield tuples containing at most ``n`` elements
    (might be less if ``fillvalue`` isn't specified).

    :param n: Number of items in every batch
    :param fillvalue: Value to fill the last batch with. If None, last batch
                      might be shorter than ``n`` elements

    :return: Iterable of batches

    .. note::

        This is an extended version of grouper() recipe
        from the :module:`itertools` module documentation.
    """
    ensure_iterable(iterable)
    if not isinstance(n, Integral):
        raise TypeError("invalid number of elements in a batch")
    if not (n > 0):
        raise ValueError("number of elements in a batch must be positive")

    # since we must use ``izip_longest``
    # (``izip`` fails if ``n`` is greater than length of ``iterable``),
    # we will apply some 'trimming' to resulting tuples if necessary
    if fillvalue is None:
        fillvalue = object()
        trimmer = lambda item: tuple(x for x in item if x is not fillvalue)
    else:
        trimmer = identity()

    args = [iter(iterable)] * n
    zipped = izip_longest(*args, fillvalue=fillvalue)
    return imap(trimmer, zipped)


def cycle(iterable, n=None):
    """Cycle through given iterable specific (or infinite) number of times.

    :param n: Number of cycles.
              If None, result cycles through ``iterable`` indefinitely.

    :return: Iterable that cycles through given one

    .. note::

        This is an extended version of ncycles() recipe
        from the :module:`itertools` module documentation
        that also has the functionality of standard :func:`itertools.cycle`.
    """
    ensure_iterable(iterable)

    if n is None:
        return cycle_(iterable)
    else:
        if not isinstance(n, Integral):
            raise TypeError("invalid number of cycles")
        if n < 0:
            raise ValueError("number of cycles cannot be negative")

        return chain.from_iterable(repeat(tuple(iterable), n))


def intertwine(*iterables):
    """Constructs an iterable which intertwines given iterables.

    The resulting iterable will return an item from first sequence,
    then from second, etc. until the last one - and then another item from
    first, then from second, etc. - up until all iterables are exhausted.
    """
    iterables = tuple(imap(ensure_iterable, iterables))

    empty = object()
    return (item
            for iterable in izip_longest(*iterables, fillvalue=empty)
            for item in iterable if item is not empty)


def iterate(iterator, n=None):
    """Efficiently advances the iterator N times; by default goes to its end.

    The actual loop is done "in C" and hence it is faster than equivalent 'for'.

    :param n: How much the iterator should be advanced.
              If None, it will be advanced until the end.
    """
    ensure_iterable(iterator)
    if n is None:
        deque(iterator, maxlen=0)
    else:
        next(islice(iterator, n, n), None)


def pad(iterable, with_=None):
    """Pad the end of given iterable with infinite sequence of given values.

    :param with_: Object to pad the iterable with. None by default.

    :return: New iterable yielding elements of given ``iterable``,
             which are then followed by infinite number of ``with_`` values
    """
    ensure_iterable(iterable)
    return chain(iterable, repeat(with_))


def unique(iterable, key=None):
    """Removes duplicates from given iterable, using given key as criterion.

    :param key: Key function which returns a hashable,
                uniquely identifying an object.

    :return: Iterable with duplicates removed
    """
    ensure_iterable(iterable)
    key = hash if key is None else ensure_callable(key)

    def generator():
        seen = set()
        for elem in iterable:
            k = key(elem)
            if k not in seen:
                seen.add(k)
                yield elem

    return generator()


# Traversal

def breadth_first(start, expand):
    """Performs a breadth-first search of a graph-like structure.

    :param start: Node to start the search from
    :param expand: Function taking a node as an argument and returning iterable
                   of its child nodes

    :return: Iterable of nodes in the BFS order

    Example::

        tree = json.loads(some_data)
        for item in breadth_first(tree, key_func('children', default=())):
            do_something_with(item)
    """
    ensure_callable(expand)

    def generator():
        queue = deque([start])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(expand(node))

    return generator()


def depth_first(start, descend):
    """Performs a depth-first search of a graph-like structure.

    :param start: Node to start the search from
    :param expand: Function taking a node as an argument and returning iterable
                   of its child nodes

    :return: Iterable of nodes in the DFS order

    Example::

        for node in depth_first(graph, attr_func('adjacent')):
            visit(node)
    """
    ensure_callable(descend)

    def generator():
        stack = [start]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(descend(node))

    return generator()


def topological_order(nodes, incoming):
    """Performs topological sort of a DAG-like structure
    (directed acyclic graph).

    :param nodes: Collection of nodes
    :param incoming: Function taking node as an argument and returning iterable
                     of nodes with edges pointing _towards_ given one

    :return: Iterable of nodes in the topological order

    .. note::

        ``incoming`` function works in _reverse_ to the typical adjacency
        relation in graphs: if ``A in incoming(B)``, it implies that ``A->B``
        is among the graph edges (**not** ``B->A``!).

        This reversal is useful in practice when dealing with graphs
        representing dependencies, module imports, header includes, and so on.

    Example::

        for package in topological_order(packages, attr_func('dependencies')):
            install(package)

    .. versionadded:: 0.0.4
    """
    ensure_iterable(nodes) ; ensure_countable(nodes)
    ensure_callable(incoming)

    # data structure for tracking node's visit state
    NOT_VISITED, VISITING, VISITED = range(3)
    visit_states = {}
    visit_state = lambda node: visit_states.get(id(node), NOT_VISITED)

    def visit(node):
        """Topological sort visitor function."""
        if visit_state(node) == VISITING:
            raise ValueError("cycle found on node %r" % (node,))
        if visit_state(node) == NOT_VISITED:
            visit_states[id(node)] = VISITING
            for neighbor in incoming(node):
                for n in visit(neighbor):
                    yield n
            visit_states[id(node)] = VISITED
            yield node

    def generator():
        """Main generator function that loops through the nodes
        until we've visited them all.
        """
        visited_count = 0
        while visited_count < len(nodes):
            visited_count = 0
            for node in nodes:
                if visit_state(node) == VISITED:
                    visited_count += 1
                else:
                    for n in visit(node):
                        yield n

    return generator()
