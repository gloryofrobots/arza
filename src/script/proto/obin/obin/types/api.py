__author__ = 'gloryofrobots'
from obin.types import space
from obin.runtime import error

"""
type conversions
"""


def tostring(obj):
    s = obj._tostring_()
    assert isinstance(s, str)
    return space.newstring(unicode(s))


def tointeger(obj):
    return space.newint(obj._tointeger_())


def tofloat(obj):
    return space.newfloat(obj._tofloat_())


def tobool(obj):
    return space.newbool(obj._tobool_())


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
    assert not space.isundefined(k)
    return obj._delete_(k)


def at(obj, k):
    assert not space.isundefined(k)
    v = obj._at_(k)
    assert v is not None
    if space.isundefined(v):
        return error.throw_2(error.Errors.KEY, obj, k)
    return v


def lookup(obj, k, default):
    v = obj._at_(k)
    assert v is not None
    if space.isundefined(v):
        return default
    return v


def slice(obj, start, end):
    v = obj._slice_(start, end)
    assert v is not None
    if space.isundefined(v):
        if space.isundefined(v):
            return error.throw_3(error.Errors.SLICE, obj, start, end)
    return v


def is_empty(obj):
    return space.newbool(n_is_empty(obj))


def n_is_empty(obj):
    return obj._length_() == 0


def n_contains_index(obj, i):
    assert space.isint(i)

    l = n_length(obj)
    if i > 0 and i < l:
        return True
    return False


def contains(obj, k):
    return space.newbool(n_contains(obj, k))


def n_contains(obj, k):
    assert not space.isundefined(k)
    v = obj._at_(k)
    if space.isundefined(v):
        return False
    else:
        return True


def put(obj, k, v):
    assert not space.isundefined(v)
    assert not space.isundefined(k)
    return obj._put_(k, v)


def at_index(obj, i):
    assert isinstance(i, int)

    v = obj._at_index_(i)
    return v


def get_index(obj, k):
    return obj._get_index_(k)


def put_at_index(obj, i, v):
    assert isinstance(i, int)
    return obj._put_at_index_(i, v)


def length(obj):
    return space.newint(n_length(obj))


def n_length(obj):
    return obj._length_()


def isempty(obj):
    return obj._length_() == 0


def iterator(obj):
    return obj._iterator_()


"""
Traits
"""


def behavior(process, obj):
    return obj._behavior_(process)


def kindof(process, obj, trait):
    return space.newbool(n_kindof(process, obj, trait))


def n_kindof(process, obj, trait):
    t = totrait(trait)
    from obin.types import behavior as _behavior
    b = behavior(process, obj)
    return _behavior.is_behavior_of(b, t)


def totrait(obj):
    if space.istrait(obj):
        return obj
    elif space.isorigin(obj):
        return obj.trait
    elif space.isentity(obj):
        return totrait(obj.source)

    error.throw_1(error.Errors.TYPE, obj)


"""
basic
"""


def n_hash(obj):
    return obj._hash_()


def clone(obj):
    c = obj._clone_()
    return c


def strict_equal(obj, other):
    return space.newbool(obj is other)


def equal(obj, other):
    return space.newbool(n_equal(obj, other))


def n_equal(obj, other):
    v = obj._equal_(other)
    return v


def compare(process, obj, other):
    if space.isuniquetype(obj):
        return error.throw_1(error.Errors.TYPE, obj)

    v = obj._compare_(other)

    return space.newint(v)


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

def put_symbol(process, obj, k, v):
    put(obj, space.newsymbol(process, k), v)


def put_native_function(process, obj, name, func, arity):
    put_symbol(process, obj, name, space.newnativefunc(space.newsymbol(process, name), func, arity))
