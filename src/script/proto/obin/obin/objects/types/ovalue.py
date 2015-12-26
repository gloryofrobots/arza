# TODO STRING LITERALS PROPER, CHARS, SYMBOLS
from oroot import W_Root, W_Hashable
from obin.objects import api


class W_ValueType(W_Root):
    pass


class W_Char(W_ValueType):
    # _immutable_fields_ = ['char_value']

    def __init__(self, value):
        self.char_value = value

    def _hash_(self):
        return self.char_value

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
        from obin.objects.space import stdlib
        return stdlib.traits.CharTraits


class W_Integer(W_ValueType):
    # _immutable_fields_ = ['int_value']

    def __init__(self, value):
        assert isinstance(value, int)
        self.int_value = value

    def _hash_(self):
        return self.int_value

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
        from obin.objects.space import stdlib
        return stdlib.traits.IntegerTraits


class W_Float(W_ValueType):
    # _immutable_fields_ = ['float_value']

    def __init__(self, value):
        assert isinstance(value, float)
        self.float_value = value

    def _hash_(self):
        from obin.utils.builtins import ohash
        return ohash(self.float_value)

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
        from obin.objects.space import stdlib
        return stdlib.traits.FloatTraits




