# TODO STRING LITERALS PROPER, CHARS, SYMBOLS
from root import W_Number
from obin.types import api

class W_Float(W_Number):
    # _immutable_fields_ = ['float_value']

    def __init__(self, value):
        assert isinstance(value, float)
        self.float_value = value

    def _hash_(self):
        from obin.utils.misc import ohash
        return ohash(self.float_value)

    def _tointeger_(self):
        return int(self.float_value)

    def _tofloat_(self):
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

    def _tostring_(self):
        return str(self.float_value)

    def _behavior_(self, process):
        return process.std.behaviors.Float




