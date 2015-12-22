__author__ = 'gloryofrobots'
from obin.runtime.exception import *


def tostring(obj):
    from space import newstring
    return newstring(unicode(obj._tostring_()))


def tointeger(obj):
    from space import newint
    return newint(obj._tointeger_())


def tofloat(obj):
    from space import newfloat
    return newfloat(obj._tofloat_())


def tobool(obj):
    from space import newbool
    return newbool(obj._tobool_())


def to_native_unicode(obj):
    return unicode(obj._tostring_())


def to_native_integer(obj):
    return obj._tointeger_()


def to_native_float(obj):
    return obj._tofloat_()


def to_native_string(obj):
    return obj._tostring_()


def to_native_bool(obj):
    return obj._tobool_()


def delete(obj, k):
    from space import isundefined
    assert not isundefined(k)
    obj._delete_(k)


def at(obj, k):
    from space import isundefined
    assert not isundefined(k)
    v = obj._at_(k)
    assert v is not None
    if isundefined(v):
        raise ObinKeyError(k)
    return v


def lookup(obj, k):
    from space import isundefined
    assert not isundefined(k)
    v = obj._lookup_(k)
    assert v is not None
    if isundefined(v):
        raise ObinKeyError(k)
    return v


def lookup_default(obj, k, default):
    from space import isundefined
    v = obj._lookup_(k)
    assert v is not None
    if isundefined(v):
        return default
    return v


def traits(obj):
    return obj._traits_()


def attach(obj, trait):
    from space import isobject, istrait
    assert isobject(obj)
    assert istrait(trait)
    obj.attach(trait)


def detach(obj, trait):
    from space import isobject, istrait
    assert isobject(obj)
    assert istrait(trait)
    obj.detach(trait)


def kindof(obj, trait):
    t = trait._totrait_()
    return obj._kindof_(t)


def has(obj, k):
    from space import isundefined, newbool
    assert not isundefined(k)
    v = obj._at_(k)
    if isundefined(v):
        return newbool(False)
    else:
        return newbool(True)


def obtain(obj, k):
    from space import isundefined, newbool
    assert not isundefined(k)
    v = obj._lookup_(k)
    if isundefined(v):
        return newbool(False)
    else:
        return newbool(True)


def length(obj):
    from space import newint
    return newint(obj._length_())


def clone(obj):
    c = obj._clone_()
    return c


def put_property(obj, k, v):
    from space import newstring
    put(obj, newstring(k), v)


def put_string_property(obj, k, v):
    from space import newstring
    put(obj, newstring(k), newstring(v))


def put(obj, k, v):
    from space import isundefined, iscell
    assert not isundefined(v)
    assert not isundefined(k)
    assert iscell(obj)
    # you can determine outer set and inner later
    if obj.isfrozen():
        raise RuntimeError("Object is frozen")

    obj._put_(k, v)


def strict_equal(obj, other):
    from space import newbool
    return newbool(obj is other)


def equal(obj, other):
    from space import newbool, isconstant
    if not isinstance(other, obj.__class__):
        return newbool(False)

    if isconstant(obj):
        return newbool(True)

    v = obj._equal_(other)
    return newbool(v)


def compare(obj, other):
    from space import isundefined, newint,  isconstant
    assert not isundefined(other)
    if isconstant(obj):
        raise ObinTypeError(obj)

    v = obj._compare_(other)

    return newint(v)


def call(obj, ctx, args):
    return obj._call_(ctx, args)


def iterator(obj):
    return obj._iterator_()


def native_iterator(obj):
    return obj._native_iterator_()


def next(obj):
    return obj._next_()


def totrait(any):
    return any._totrait_()


def new_native_function(function, name, arity):
    from obin.objects.space import newprimitive, newstring
    assert isinstance(name, unicode)
    obj = newprimitive(newstring(name), function, arity)
    return obj


# 15
def put_native_function(obj, name, func, arity):
    put_property(obj, name, new_native_function(func, name, arity))
