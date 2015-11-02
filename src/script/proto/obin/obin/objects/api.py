__author__ = 'gloryofrobots'


def tostring(obj):
    return obj._tostring_()


def tobool(obj):
    return obj._tobool_()


def delete(obj, k):
    from object_space import isundefined
    assert not isundefined(k)
    obj._delete_(k)


def at(obj, k):
    from object_space import isundefined
    assert not isundefined(k)
    return obj._at_(k)


def length(obj):
    return obj._length_()


def put(obj, k, v):
    from object_space import isundefined
    assert not isundefined(v)
    assert not isundefined(k)
    obj._put_(k, v)


def equal(obj, other):
    return obj._equal_(other)


def compare(obj, other):
    from object_space import isundefined
    assert not isundefined(other)
    return obj._compare_(other)


def next(obj):
    return obj._next_()
