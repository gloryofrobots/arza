# TODO STRING LITERALS PROPER, CHARS, SYMBOLS
from root import W_Root


class W_ValueType(W_Root):
    pass


class W_Char(W_ValueType):
    # _immutable_fields_ = ['char_value']

    def __init__(self, value):
        self.char_value = value

    def __str__(self):
        return "%s" % (chr(self.char_value),)

    def _tostring_(self):
        return chr(self.char_value)

    def _equal_(self, other):
        assert isinstance(other, W_Char)
        return self.char_value == other.char_value

    def _compare_(self, other):
        assert isinstance(other, W_Char)
        if self.char_value > other.char_value:
            return 1
        elif self.char_value < other.char_value:
            return -1
        else:
            return 0

    def _tobool_(self):
        return bool(self.char_value)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.CharTraits


class W_Integer(W_ValueType):
    # _immutable_fields_ = ['int_value']

    def __init__(self, value):
        assert isinstance(value, int)
        self.int_value = value

    def _tointeger_(self):
        return self.int_value

    def _tofloat_(self):
        return float(self.int_value)

    def _equal_(self, other):
        assert isinstance(other, W_Integer)
        return self.int_value == other.int_value

    def _compare_(self, other):
        assert isinstance(other, W_Integer)
        if self.int_value > other.int_value:
            return 1
        elif self.int_value < other.int_value:
            return -1
        else:
            return 0

    def _tostring_(self):
        return str(self.int_value)

    def _tobool_(self):
        return bool(self.int_value)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.IntegerTraits


class W_Float(W_ValueType):
    # _immutable_fields_ = ['float_value']

    def __init__(self, value):
        assert isinstance(value, float)
        self.float_value = value

    def _tointeger_(self):
        return int(self.float_value)

    def _tofloat_(self):
        return self.float_value

    def _equal_(self, other):
        assert isinstance(other, W_Float)
        return self.float_value == other.float_value

    def _compare_(self, other):
        assert isinstance(other, W_Float)
        if self.float_value > other.float_value:
            return 1
        elif self.float_value < other.float_value:
            return -1
        else:
            return 0

    def _tostring_(self):
        return str(self.float_value)

    def _tobool_(self):
        return bool(self.float_value)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.FloatTraits


class StringIterator(W_ValueType):
    def __init__(self, source, length):
        assert isinstance(source, W_String)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self._string_length = length

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self._string_length:
            return newundefined()

        el = self.source.at(self.index)
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self._string_length)

    def _tobool_(self):
        if self.index >= self._string_length:
            return False
        return True


class W_String(W_ValueType):
    # _immutable_fields_ = ['value']

    def __init__(self, value):
        assert value is not None and isinstance(value, unicode)
        self.string_value = value
        self.__length = len(self.string_value)

    def _equal_(self, other):
        assert isinstance(other, W_String)
        return self.string_value == other.string_value

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
        return self.string_value.__hash__()

    def isempty(self):
        return not bool(len(self.string_value))

    def _tostring_(self):
        return str(self.string_value)

    def _iterator_(self):
        return StringIterator(self, self.__length)

    def _tobool_(self):
        return bool(self.string_value)

    def _length_(self):
        return self.__length

    def at(self, index):
        from obin.objects.space import newundefined, newstring
        from obin.runtime.exception import ObinKeyError
        try:
            ch = self.string_value[index]
        except ObinKeyError:
            return newundefined()

        return newstring(ch)

    def _at_(self, index):
        from obin.objects.space import isint
        from obin.objects import api
        assert isint(index)
        return self.at(api.to_native_integer(index))

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.StringTraits
