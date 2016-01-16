from obin.types.root import W_Hashable
from sequence import W_SequenceIterator
# from obin.runtime.error import *
# from obin.objects import api

class W_String(W_Hashable):
    # _immutable_fields_ = ['value']

    def __init__(self, value):
        W_Hashable.__init__(self)
        assert value is not None and isinstance(value, unicode)
        self.string_value = value
        self.__length = len(self.string_value)

    def _compute_hash_(self):
        """The algorithm behind compute_hash() for a string or a unicode."""
        from rpython.rlib.rarithmetic import intmask
        length = len(self.string_value)
        if length == 0:
            return -1
        x = ord(self.string_value[0]) << 7
        i = 0
        while i < length:
            x = intmask((1000003 * x) ^ ord(self.string_value[i]))
            i += 1
        x ^= length
        return intmask(x)

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

    def _tostring_(self):
        return str(self.string_value)

    def _iterator_(self):
        return W_SequenceIterator(self)

    def _tobool_(self):
        return bool(self.string_value)

    def _length_(self):
        return self.__length

    def _at_index_(self, i):
        from obin.types.space import newundefined, newchar
        try:
            ch = self.string_value[i]
        except:
            return newundefined()

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
        return self._at_index_(api.to_native_integer(index))

    def _behavior_(self, process):
        return process.std.behaviors.String
