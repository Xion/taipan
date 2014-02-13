"""
Set-related functions and classes.
"""
from itertools import chain, combinations
from numbers import Integral

from taipan._compat import imap, xrange
from taipan.collections import ensure_countable, is_set
from taipan.collections.tuples import is_tuple


__all__ = ['k_subsets', 'power', 'powerset', 'trivial_partition']


def k_subsets(set_, k):
    """Return subsets of given set with given cardinality.
    :param k: Cardinality of subsets to return
    :return: Iterable containing all ``k``-subsets of given set
    """
    ensure_countable(set_)

    if not isinstance(k, Integral):
        raise TypeError("subset cardinality must be a number")
    if not (k >= 0):
        raise ValueError("subset cardinality must be positive")
    if not (k <= len(set_)):
        raise ValueError("subset cardinality must not exceed set cardinality")

    result = combinations(set_, k)
    return _harmonize_subset_types(set_, result)


def power(set_):
    """Returns all subsets of given set.

    :return: Powerset of given set, i.e. iterable containing all its subsets,
             sorted by ascending cardinality.
    """
    ensure_countable(set_)

    result = chain.from_iterable(combinations(set_, r)
                                 for r in xrange(len(set_) + 1))
    return _harmonize_subset_types(set_, result)

#: Alias for :func:`power`.
powerset = power


def trivial_partition(set_):
    """Returns a parition of given set into 1-element subsets.

    :return: Trivial partition of given set, i.e. iterable containing disjoint
             1-element sets, each consisting of a single element
             from given set
    """
    ensure_countable(set_)

    result = ((x,) for x in set_)
    return _harmonize_subset_types(set_, result)


# Utility functions

def _harmonize_subset_types(set_, subset_tuples):
    """Possibly convert an iterable of tuples with subsets of given "set",
    to an iterable of :class:`set` objects if original "set" was so too.
    """
    # if argument is originally a set, return subsets also as sets;
    # otherwise (for non-set collection), return subsets as tuples
    if is_tuple(set_):
        return subset_tuples
    else:
        subset_class = set_.__class__ if is_set(set_) else tuple
        return imap(subset_class, subset_tuples)
