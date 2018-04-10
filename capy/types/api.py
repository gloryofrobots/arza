# TODO REMOVE UNNECESSARRY ASSERTS OR REPLACE THEM WITH DEBUG MODE

from capy.types import space
from capy.runtime import error

DEBUG_MODE = False


# UGLY DEBUGGING HACKS
class Debug:
    def __init__(self):
        self._BREAKPOINTS = []

    def pbp(self, bp, *args):
        # print if breakpoint set
        if not self.has_bp(bp):
            return
        self._p(args)

    def pd(self, *args):
        # print if debug_mode True
        if not DEBUG_MODE:
            return
        self._p(args)

    def _p(self, args):
        print " ".join(map(str, args))

    def add_bp(self, num):
        self._BREAKPOINTS.append(num)

    def has_bp(self, bp):
        # if you need to enable all pbp prints set bp to -1
        return bp in self._BREAKPOINTS or bp == -1


d = Debug()


# *************************
# type conversions
# **************************************

# PYTHON TYPES
def to_u(obj):
    return unicode(obj._to_string_())


def to_i(obj):
    return obj._to_integer_()


def to_f(obj):
    return obj._to_float_()


def to_s(obj):
    s = obj._to_string_()
    if not isinstance(s, str):
        s = obj._to_string_()
        assert isinstance(s, str), (s, obj)
    return s


def to_r(obj):
    s = obj._to_repr_()
    assert isinstance(s, str)
    return s


def to_b(obj):
    if obj is space.w_True:
        return True
    elif obj is space.w_False:
        return False

    error.throw_2(error.Errors.TYPE_ERROR, space.newstring(u"Bool expected"), obj)


def to_string(obj):
    s = obj._to_string_()
    assert isinstance(s, str)
    return space.newstring(unicode(s))


def to_repr(obj):
    s = obj._to_repr_()
    assert isinstance(s, str)
    return space.newstring(unicode(s))


def to_integer(obj):
    return space.newint(obj._to_integer_())


def to_float(obj):
    return space.newfloat(obj._to_float_())


def to_bool(obj):
    return space.newbool(to_b(obj))


"""
collection stuff
"""


def delete(obj, k):
    assert not space.isvoid(k)
    return obj._delete_(k)


def at(obj, k):
    assert not space.isvoid(k)
    v = obj._at_(k)
    assert v is not None
    if space.isvoid(v):
        return error.throw_2(error.Errors.KEY_ERROR, k, obj)
    return v


def lookup(obj, k, default):
    v = obj._at_(k)
    assert v is not None
    if space.isvoid(v):
        return default
    return v


def lookup_symbol(process, obj, k):
    if not space.isvaluetype(obj):
        val = lookup(obj, k, space.newvoid())
        if not space.isvoid(val):
            return val

    _type = get_type(process, obj)
    val = _type.lookup_symbol(k)
    if space.isvoid(val):
        return error.throw_2(error.Errors.KEY_ERROR, obj, k)
    return val


def is_empty(obj):
    return space.newbool(is_empty_b(obj))


def is_empty_b(obj):
    from capy.types import plist
    if space.islist(obj):
        return plist.is_empty(obj)

    return obj._is_empty_()


def contains_index_b(obj, i):
    assert space.isint(i)

    l = length_i(obj)
    if i > 0 and i < l:
        return True
    return False


def has(obj, k):
    return space.newbool(has_b(obj, k))


def has_b(obj, k):
    assert not space.isvoid(k)
    v = obj._has_(k)
    assert isinstance(v, bool)
    return v


def notin(k, obj):
    return space.newbool(not has_b(obj, k))


def put(obj, k, v):
    assert not space.isvoid(v)
    assert not space.isvoid(k)
    return obj._put_(k, v)


def at_index(obj, i):
    assert isinstance(i, int)
    v = obj._at_index_(i)

    # if space.isvoid(v):
    #     return error.throw_2(error.Errors.KEY_ERROR, space.newint(i), obj)

    return v


def first(obj):
    return at_index(obj, 0)


def second(obj):
    return at_index(obj, 1)


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


"""
Traits
"""


def get_type(process, obj):
    return obj._type_(process)


def kindof(process, obj, trait):
    assert not space.islist(trait)
    return space.newbool(kindof_b(process, obj, trait))


def kindof_b(process, obj, kind):
    if not space.isclass(kind):
        return error.throw_3(error.Errors.TYPE_ERROR, obj, kind, space.newstring(u"Expecting class"))
    t = get_type(process, obj)
    return equal_b(t, kind)

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


# def compare(process, obj, other):
#     if space.isuniquetype(obj):
#         return error.throw_2(error.Errors.TYPE, obj, space.newstring(u"Unique expected"))
#
#     v = obj._compare_(other)
#
#     return space.newint(v)


def seq(obj):
    return obj._seq_()


def head(obj):
    return obj._head_()


def tail(obj):
    return obj._tail_()


"""
Callable
"""


def call(process, obj, args):
    assert space.isarray(args) or space.isarguments(args)
    return obj._call_(process, args)


def to_routine(obj, stack, args):
    assert space.isarray(args) or space.isarguments(args), (args, args.__class__.__name__)
    return obj._to_routine_(stack, args)


"""
put helpers
"""


def put_symbol(process, obj, k, v):
    put(obj, space.newsymbol(process, k), v)


def put_native_function(process, obj, name, func, arity):
    put_symbol(process, obj, name, space.newnativefunc(space.newsymbol(process, name), func, arity))


def put_native_method(process, obj, name, func, arity):
    put_symbol(process, obj, name, space.newnativemethod(space.newsymbol(process, name), func, arity))
