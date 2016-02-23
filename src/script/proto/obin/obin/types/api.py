__author__ = 'gloryofrobots'
from obin.types import space
from obin.runtime import error

"""
type conversions
"""


def to_string(obj):
    s = obj._to_string_()
    assert isinstance(s, str)
    return space.newstring(unicode(s))


def to_integer(obj):
    return space.newint(obj._to_integer_())


def to_float(obj):
    return space.newfloat(obj._to_float_())


def to_bool(obj):
    return space.newbool(obj._to_bool_())


"""
PYTHON TYPES
"""


# TODO REMOVE UNNECESSARRY ASSERTS OR REPLACE THEM WITH DEBUG MODE

def to_u(obj):
    return unicode(obj._to_string_())


def to_i(obj):
    return obj._to_integer_()


def to_f(obj):
    return obj._to_float_()


def to_s(obj):
    s = obj._to_string_()
    assert isinstance(s, str)
    return s


def to_b(obj):
    return obj._to_bool_()


"""
collection stuff
"""


def delete(obj, k):
    assert not space.isnil(k)
    return obj._delete_(k)


def at(obj, k):
    assert not space.isnil(k)
    v = obj._at_(k)
    assert v is not None
    if space.isnil(v):
        return error.throw_2(error.Errors.KEY_ERROR, k, obj)
    return v


def lookup(obj, k, default):
    v = obj._at_(k)
    assert v is not None
    if space.isnil(v):
        return default
    return v


def slice(obj, start, end):
    v = obj._slice_(start, end)
    assert v is not None
    if space.isnil(v):
        return error.throw_3(error.Errors.SLICE, obj, start, end)
    return v


def is_empty(obj):
    return space.newbool(is_empty_b(obj))


def is_empty_b(obj):
    return obj._length_() == 0


def contains_index_b(obj, i):
    assert space.isint(i)

    l = length_i(obj)
    if i > 0 and i < l:
        return True
    return False


def in_(k, obj):
    return space.newbool(in_b(obj, k))


def in_b(obj, k):
    assert not space.isnil(k)
    v = obj._contains_(k)
    assert isinstance(v, bool)
    return v


def notin(k, obj):
    return space.newbool(not in_b(obj, k))


def put(obj, k, v):
    assert not space.isnil(v)
    assert not space.isnil(k)
    return obj._put_(k, v)


def at_index(obj, i):
    assert isinstance(i, int)
    if obj is None:
        print obj
    v = obj._at_index_(i)
    return v


def get_index(obj, k):
    return obj._get_index_(k)


def put_at_index(obj, i, v):
    assert isinstance(i, int)
    return obj._put_at_index_(i, v)


def length(obj):
    return space.newint(length_i(obj))


def length_i(obj):
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


def traits(process, obj):
    b = behavior(process, obj)
    return b.traits


def kindof(process, obj, trait):
    return space.newbool(n_kindof(process, obj, trait))


def kindof_list(process, obj, traits):
    from obin.types import behavior as _behavior
    assert space.islist(traits)

    b = behavior(process, obj)
    return space.newbool(_behavior.has_traits(b, traits))


def n_kindof(process, obj, trait):
    t = totrait(trait)
    from obin.types import behavior as _behavior
    b = behavior(process, obj)
    return _behavior.is_behavior_of(b, t)


def totrait(obj):
    if space.istrait(obj):
        return obj
    elif space.isentity(obj):
        return totrait(obj.source)

    error.throw_1(error.Errors.TYPE, obj)


"""
basic
"""


def hash_i(obj):
    return obj._hash_()


def clone(obj):
    c = obj._clone_()
    return c


def is_(obj, other):
    return space.newbool(obj is other)


def not_(obj):
    return space.newbool(not to_b(obj))


def isnot(obj, other):
    return space.newbool(obj is not other)


def equal(obj, other):
    res = equal_b(obj, other)
    return space.newbool(res)


def equal_b(obj, other):
    v = obj._equal_(other)
    return v


def not_equal(obj, other):
    v = obj._equal_(other)
    return space.newbool(not v)


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
put helpers
"""


def put_symbol(process, obj, k, v):
    put(obj, space.newsymbol(process, k), v)


def put_native_function(process, obj, name, func, arity):
    put_symbol(process, obj, name, space.newnativefunc(space.newsymbol(process, name), func, arity))
