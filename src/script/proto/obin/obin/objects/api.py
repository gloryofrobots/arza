__author__ = 'gloryofrobots'

"""
type conversions
"""


def tostring(obj):
    from space import newstring
    s = obj._tostring_()
    assert isinstance(s, str)
    return newstring(unicode(s))


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
    s = obj._tostring_()
    assert isinstance(s, str)
    return s


def to_native_bool(obj):
    return obj._tobool_()


"""
collection stuff
"""


def delete(obj, k):
    from space import isundefined
    assert not isundefined(k)
    obj._delete_(k)


def at(obj, k):
    from obin.runtime.error import ObinKeyError
    from space import isundefined
    assert not isundefined(k)
    v = obj._at_(k)
    assert v is not None
    if isundefined(v):
        raise ObinKeyError(k)
    return v


def lookup(obj, k, default):
    from space import isundefined
    v = obj._at_(k)
    assert v is not None
    if isundefined(v):
        return default
    return v


def slice(obj, start, end, step):
    from obin.runtime.error import ObinSliceError
    from space import isundefined
    v = obj._slice_(start, end, step)
    assert v is not None
    if isundefined(v):
        raise ObinSliceError(start, end, step)
    return v


def is_empty(obj):
    from space import newbool
    return newbool(n_is_empty(obj))


def n_is_empty(obj):
    return obj._length_() == 0


def n_contains_index(obj, i):
    from space import isint
    assert isint(i)

    l = n_length(obj)
    if i > 0 and i < l:
        return True
    return False


def contains(obj, k):
    from space import newbool
    return newbool(n_contains(obj, k))


def n_contains(obj, k):
    from space import isundefined
    assert not isundefined(k)
    v = obj._at_(k)
    if isundefined(v):
        return False
    else:
        return True


def put_string(obj, k, v):
    from space import newstring
    put(obj, newstring(k), v)


def put_string_string(obj, k, v):
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


def at_index(obj, i):
    from obin.runtime.error import ObinKeyError
    from space import isundefined
    assert isinstance(i, int)

    v = obj._at_index_(i)
    return v

def get_index(obj, k):
    return obj._get_index_(k)


def put_at_index(obj, i, v):
    assert isinstance(i, int)
    return obj._put_at_index_(i, v)


def length(obj):
    from space import newint
    return newint(n_length(obj))


def n_length(obj):
    return obj._length_()


def iterator(obj):
    return obj._iterator_()




"""
Traits
"""

def behavior(process, obj):
    return obj._behavior_(process)

def kindof(obj, trait):
    raise NotImplementedError()
    from space import newbool
    return newbool(n_kindof(obj, trait))


def n_kindof(obj, trait):
    raise NotImplementedError()
    t = totrait(trait)
    return obj._kindof_(t)


def totrait(obj):
    from space import isorigin, istrait, isentity
    if istrait(obj):
        return obj
    elif isorigin(obj):
        return obj.trait
    elif isentity(obj):
        return totrait(obj.source)

    raise RuntimeError("Object can not be represented as trait")


"""
basic
"""


def n_hash(obj):
    return obj._hash_()


def clone(obj):
    c = obj._clone_()
    return c


def strict_equal(obj, other):
    from space import newbool
    return newbool(obj is other)


def equal(obj, other):
    from space import newbool
    return newbool(n_equal(obj, other))


def n_equal(obj, other):
    from space import isconstant
    if not isinstance(other, obj.__class__):
        return False

    if isconstant(obj):
        return True

    v = obj._equal_(other)
    return v


def compare(obj, other):
    from obin.runtime.error import ObinTypeError
    from space import isundefined, newint, isconstant
    assert not isundefined(other)
    if isconstant(obj):
        raise ObinTypeError(obj)

    v = obj._compare_(other)

    return newint(v)


def next(obj):
    return obj._next_()


"""
Callable
"""


def call(process, obj, args):
    return obj._call_(process, args)


def to_routine(obj, stack, args):
    return obj._to_routine_(stack, args)


"""
native funcs
"""

# TODO move to object
def put_native_function(obj, name, func, arity):
    from obin.objects.space import newnativefunc, newstring
    put_string(obj, name, newnativefunc(newstring(name), func, arity))
