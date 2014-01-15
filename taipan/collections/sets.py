"""
Set-related functions and classes.
"""
from itertools import chain, combinations

from taipan._compat import imap, xrange
from taipan.collections import ensure_countable, is_set
from taipan.collections.tuples import is_tuple


def power(set_):
    """Returns all subsets of given set.

    :return: Powerset of given set, i.e. iterable containing all its subsets,
             sorted by ascending cardinality.
    """
    ensure_countable(set_)

    result = chain.from_iterable(combinations(set_, r)
                                 for r in xrange(len(set_) + 1))

    # if argument is originally a set, return subsets also as sets;
    # otherwise (for non-set collection), return subsets as tuples
    if is_tuple(set_):
        return result  # combinations() returns tuples; need not convert them
    else:
        subset_class = set_.__class__ if is_set(set_) else tuple
        return imap(subset_class, result)
