"""
Decorators for skipping tests.
"""
from taipan.functional.functions import identity
from taipan.testing._unittest import skip


__all__ = [
    'skipIfReturnsTrue', 'skipUnlessReturnsTrue',
    'skipIfReturnsFalse', 'skipUnlessReturnsFalse',
    'skipIfHasattr', 'skipUnlessHasattr',
]


# TODO(xion): come up with better name
def skipIfReturnsTrue(predicate):
    """Decorator that will cause a test to be skipped
    if given ``predicate`` callable evaluates to true.
    """
    if predicate():
        desc = getattr(predicate, '__doc__', None) or repr(predicate)
        return skip("predicate evaluated to true: %s" % desc)
    return identity()


def skipUnlessReturnsTrue(predicate):
    """Decorator that will cause a test to be skipped
    unless given ``predicate`` callable evaluates to true.
    """
    if not predicate():
        desc = getattr(predicate, '__doc__', None) or repr(predicate)
        return skip("predicate evaluated to false: %s" % desc)
    return identity()

# TODO(xion): seriously weigh pros & cons of having those
skipIfReturnsFalse = skipUnlessReturnsTrue
skipUnlessReturnsFalse = skipIfReturnsTrue


def skipIfHasattr(obj, attr):
    """Decorator that will cause a test to be skipped
    if given ``object`` contains given ``attr``\ ibute.
    """
    if hasattr(obj, attr):
        return skip("%r has attribute %r" % (obj, attr))
    return identity()


def skipUnlessHasattr(obj, attr):
    """Decorator that will cause a test to be skipped
    unless given ``object`` contains given ``attr``\ ibute.
    """
    if not hasattr(obj, attr):
        return skip("%r does not have attribute %r" % (obj, attr))
    return identity()
