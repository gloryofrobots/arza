from root import W_ValueType
from obin.types import api

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
        try:
            val = api.to_i(other)
            return self.int_value == val
        except:
            return False

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

    def _behavior_(self, process):
        return process.std.behaviors.Integer


