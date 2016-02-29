from root import W_ValueType


class W_Char(W_ValueType):
    # _immutable_fields_ = ['char_value']

    def __init__(self, value):
        self.char_value = value

    def _hash_(self):
        return self.char_value

    def __str__(self):
        return "%s" % (chr(self.char_value),)

    def _to_string_(self):
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

    def _type_(self, process):
        return process.std.types.Char

