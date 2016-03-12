from obin.types.root import W_Hashable
from sequence import W_SequenceIterator
from obin.types import api, space
from obin.runtime import error


# from obin.types import plist
# from obin.types import space
# from obin.runtime.error import *


class W_String(W_Hashable):
    # _immutable_fields_ = ['value']

    def __init__(self, value):
        W_Hashable.__init__(self)
        assert value is not None and isinstance(value, unicode)
        self.string_value = value
        self.__length = len(self.string_value)

    def _compute_hash_(self):
        """The algorithm behind compute_hash() for a string or a unicode."""
        from obin.misc.platform import rarithmetic
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
        from obin.types import space
        if space.issymbol(other):
            return self._equal_(other.string)

        if not space.isstring(other):
            return False

        return self.string_value == other.string_value

    def isempty(self):
        return not bool(len(self.string_value))

    def _to_string_(self):
        return str(self.string_value)

    def _iterator_(self):
        return W_SequenceIterator(self)

    def _length_(self):
        return self.__length

    def _at_index_(self, i):
        from obin.types.space import newvoid, newchar
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
        from obin.types.space import isint
        from obin.types import api
        assert isint(index)
        return self._at_index_(api.to_i(index))

    def _type_(self, process):
        return process.std.types.String


def slice(s, first, last):
    error.affirm_type(s, space.isstring)
    assert isinstance(first, int)
    assert isinstance(last, int)
    return W_String(s.string_value[first:last])


def take(s, count):
    error.affirm_type(s, space.isstring)
    assert isinstance(count, int)
    return W_String(s.string_value[:count])


def drop(s, count):
    error.affirm_type(s, space.isstring)
    assert isinstance(count, int)
    return W_String(s.string_value[count:])


def concat(l, r):
    error.affirm_type(l, space.isstring)
    error.affirm_type(r, space.isstring)
    sleft = api.to_u(l)
    sright = api.to_u(r)
    return W_String(sleft + sright)


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
