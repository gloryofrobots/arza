# TODO STRING LITERALS PROPER, CHARS, SYMBOLS
from root import W_Number
from obin.types import api
from obin.misc import platform

class W_Float(W_Number):
    # _immutable_fields_ = ['float_value']

    def __init__(self, value):
        assert isinstance(value, float)
        self.float_value = value

    def _hash_(self):
        return platform.obin_hash(self.float_value)

    def _to_integer_(self):
        return int(self.float_value)

    def _to_float_(self):
        return self.float_value

    def _equal_(self, other):
        try:
            fother = api.to_f(other)
            return self.float_value == fother
        except:
            return False

    def _compare_(self, other):
        assert isinstance(other, W_Float)
        if self.float_value > other.float_value:
            return 1
        elif self.float_value < other.float_value:
            return -1
        else:
            return 0

    def _to_string_(self):
        return str(self.float_value)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.Float




