from root import W_ValueType
from arza.types import api, space
from arza.runtime import error


class W_Integer(W_ValueType):
    # _immutable_fields_ = ['int_value']

    def __init__(self, value):
        assert isinstance(value, int) or isinstance(value, long), (value, value.__class__.__name__)
        self.int_value = value

    def _hash_(self):
        return self.int_value

    def _to_integer_(self):
        return self.int_value

    def _to_float_(self):
        return float(self.int_value)

    def _equal_(self, other):
        if not space.isnumber(other):
            return False
        val = api.to_i(other)
        return self.int_value == val

    def _compare_(self, other):
        assert isinstance(other, W_Integer)
        if self.int_value > other.int_value:
            return 1
        elif self.int_value < other.int_value:
            return -1
        else:
            return 0

    def _to_string_(self):
        return str(self.int_value)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.classes.Int
