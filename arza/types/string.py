from arza.types.root import W_Hashable
from arza.types import api, space
from arza.runtime import error


class W_String(W_Hashable):
    # _immutable_fields_ = ['value']

    def __init__(self, value):
        W_Hashable.__init__(self)
        assert value is not None and isinstance(value, unicode)
        self.string_value = value
        self.length = len(self.string_value)

    def _compute_hash_(self):
        """The algorithm behind compute_hash() for a string or a unicode."""
        from arza.misc.platform import rarithmetic
        length = len(self.string_value)
        if length == 0:
            return -1
        x = ord(self.string_value[0]) << 7
        i = 0
        while i < length:
            x = rarithmetic.intmask((1000003 * x) ^ ord(self.string_value[i]))
            i += 1
        x ^= length
        return rarithmetic.intmask(x)

    def _compare_(self, other):
        assert isinstance(other, W_String)
        if self.string_value > other.string_value:
            return 1
        elif self.string_value < other.string_value:
            return -1
        else:
            return 0

    def __eq__(self, other):
        if not isinstance(other, W_String):
            return False
        return self._equal_(other)

    def __hash__(self):
        return self._hash_()

    def _equal_(self, other):
        from arza.types import space
        if space.issymbol(other):
            return self._equal_(other.string)

        if not space.isstring(other):
            return False

        return self.string_value == other.string_value

    def isempty(self):
        return not bool(len(self.string_value))

    def _to_string_(self):
        return str(self.string_value)

    def _to_repr_(self):
        return str(u"\"%s\"" % self.string_value)

    def _length_(self):
        return self.length

    def _at_index_(self, i):
        from arza.types.space import newvoid, newchar
        try:
            ch = self.string_value[i]
        except:
            return newvoid()

        return newchar(ch)

    def _get_index_(self, obj):
        try:
            return self.string_value.index(obj)
        except ValueError:
            return -1

    def _at_(self, index):
        from arza.types.space import isint
        from arza.types import api
        assert isint(index)
        return self._at_index_(api.to_i(index))

    def _type_(self, process):
        return process.std.types.String

    def to_l(self):
        return [space.newchar(c) for c in self.string_value]

    def to_list(self):
        return space.newlist(self.to_l())


def to_list(s):
    error.affirm_type(s, space.isstring)
    return s.to_list()


def slice(s, first, last):
    error.affirm_type(s, space.isstring)
    assert isinstance(first, int)
    assert isinstance(last, int)
    if first < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"First index < 0"), space.newint(first))
    if first >= last:
        error.throw_3(error.Errors.SLICE_ERROR, space.newstring(u"First index >= Last index"),
                      space.newint(first), space.newint(last))
    if last >= s.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Last index too big"), space.newint(last))
    return W_String(s.string_value[first:last])


def take(s, count):
    error.affirm_type(s, space.isstring)
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= s.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))

    return W_String(s.string_value[:count])


def drop(s, count):
    error.affirm_type(s, space.isstring)
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= s.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))

    return W_String(s.string_value[count:])


def _replace(s, old, new, count):
    error.affirm_type(s, space.isstring)
    error.affirm_type(old, space.isstring)
    error.affirm_type(new, space.isstring)
    su = api.to_u(s)
    oldu = api.to_u(old)
    newu = api.to_u(new)
    su.string_value.replace(oldu, newu, count)


def replace(s, old, new):
    _replace(s, old, new, -1)


def replace_first(s, old, new):
    _replace(s, old, new, 1)


def concat(l, r):
    error.affirm_type(l, space.isstring)
    error.affirm_type(r, space.isstring)
    sleft = api.to_u(l)
    sright = api.to_u(r)
    return W_String(sleft + sright)


def split(s, sep):
    error.affirm_type(s, space.isstring)
    error.affirm_type(sep, space.isstring)

    return space.newlist([space.newstring(chunk) for chunk in s.string_value.split(sep.string_value)])


def append(s, c):
    error.affirm_type(s, space.isstring)
    error.affirm_type(c, space.ischar)

    return W_String(s.string_value + unichr(c.char_value))


def prepend(s, c):
    error.affirm_type(s, space.isstring)
    error.affirm_type(c, space.ischar)

    return W_String(unichr(c.char_value) + s.string_value)


def reverse(s):
    error.affirm_type(s, space.isstring)
    return W_String(s.string_value[::-1])


class Builder:
    def __init__(self):
        self.els = []

    def nl(self):
        self.els.append(u"\n")
        return self

    def space(self, count=1):
        self.els.append(u" " * count)
        return self

    def tab(self):
        self.els.append(u"    ")
        return self

    def add(self, obj):
        self.els.append(api.to_u(obj))
        return self

    def add_u(self, unistr):
        assert isinstance(unistr, unicode)
        self.els.append(unicode(unistr))
        return self

    def value(self):
        res = u"".join(self.els)
        return W_String(res)
