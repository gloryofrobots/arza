from obin.types import  space, api, root

class W_Char(root.W_ValueType):
    def __init__(self, value):
        self.char_value = value

    def _hash_(self):
        return self.char_value

    def __str__(self):
        return "%s" % (chr(self.char_value),)

    def _to_string_(self):
        return chr(self.char_value)

    def _to_repr_(self):
        return "'%s'" % self._to_string_()

    def _equal_(self, other):
        if not space.ischar(other):
            return False

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

