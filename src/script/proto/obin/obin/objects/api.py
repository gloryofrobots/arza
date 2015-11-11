__author__ = 'gloryofrobots'
from obin.runtime.exception import *


def tostring(obj):
    from object_space import newstring
    return newstring(unicode(obj._tostring_()))


def tobool(obj):
    from object_space import newbool
    return newbool(obj._tobool_())


def delete(obj, k):
    from object_space import isundefined
    assert not isundefined(k)
    obj._delete_(k)


def at(obj, k):
    from object_space import isundefined
    assert not isundefined(k)
    v = obj._at_(k)
    assert v is not None
    if isundefined(v):
        raise ObinKeyError(k)
    return v


def lookup(obj, k):
    from object_space import isundefined
    assert not isundefined(k)
    v = obj._lookup_(k)
    assert v is not None
    if isundefined(v):
        raise ObinKeyError(k)
    return v


def has(obj, k):
    from object_space import isundefined, newbool
    assert not isundefined(k)
    v = obj._at_(k)
    if isundefined(v):
        return newbool(False)
    else:
        return newbool(True)


def obtain(obj, k):
    from object_space import isundefined, newbool
    assert not isundefined(k)
    v = obj._lookup_(k)
    if isundefined(v):
        return newbool(False)
    else:
        return newbool(True)


def length(obj):
    from object_space import newint
    return newint(obj._length_())


def clone(obj):
    c = obj._clone_()
    return c


def put_property(obj, k, v):
    from object_space import newstring
    put(obj, newstring(k), v)


def put(obj, k, v):
    from object_space import isundefined, iscell
    assert not isundefined(v)
    assert not isundefined(k)
    assert iscell(obj)
    # you can determine outer set and inner later
    if obj.isfrozen():
        raise RuntimeError("Object is frozen")

    obj._put_(k, v)


def strict_equal(obj, other):
    from object_space import newbool, isvaluetype, isconstant
    if not isinstance(other, obj.__class__):
        return newbool(False)
    if isconstant(obj):
        return newbool(True)

    if isvaluetype(obj):
        return newbool(obj.value() is other.value())

    return newbool(obj is other)


def equal(obj, other):
    from object_space import newbool, isvaluetype, isconstant
    if not isinstance(other, obj.__class__):
        return newbool(False)

    if isvaluetype(obj):
        return newbool(obj.value() == other.value())

    if isconstant(obj):
        return newbool(True)

    v = obj._equal_(other)
    return newbool(v)


def compare(obj, other):
    from object_space import isundefined, newint, newbool, isvaluetype, isconstant
    assert not isundefined(other)
    v = obj._compare_(other)
    if isvaluetype(obj):
        return newint(cmp(obj.value(), other.value()))

    if isconstant(obj):
        raise ObinTypeError(obj)

    return newint(v)


def call(obj, ctx, args):
    return obj._call_(ctx, args)

def iterator(obj):
    return obj._iterator_()

def next(obj):
    return obj._next_()


def new_native_function(function, name):
    from obin.objects.object_space import newprimitive, newstring
    assert isinstance(name, unicode)
    obj = newprimitive(newstring(name), function)
    return obj


# 15
def put_native_function(obj, name, func):
    put_property(obj, name, new_native_function(func, name))
