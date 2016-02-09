from obin.types import api, space
from obin.types.root import W_Any
from obin.types.string import W_String
from obin.runtime import error

class W_Symbol(W_Any):
    # _immutable_fields_ = ['value']

    def __init__(self, string, idx):
        self.idx = idx
        self.string = string
        self.repr = ":%s" % api.to_s(self.string)

    def __eq__(self, other):
        return self._equal_(other)

    def __hash__(self):
        return self._hash_()

    def _hash_(self):
        return self.string._hash_()

    def _equal_(self, other):
        from obin.types import space
        if space.issymbol(other):
            val = self.idx == other.idx
            # print "SYMBOL EQ", self, other, val
            return val

        arg = string_or_symbol_string(other)
        if arg is None:
            # print "SYMBOL NOT EQ", self, other
            return False

        val = self.string._equal_(arg)
        # print "SYMBOL EQ STRING VAL", self, other, val
        return val

    def _compare_(self, other):
        arg = string_or_symbol_string(other)
        if arg is None:
            return error.throw_3(error.Errors.NOT_IMPLEMENTED, space.newstring(u"_compare_"), self, other)

        return self.string._compare_(arg)

    def _to_string_(self):
        return api.to_s(self.string)

    def _iterator_(self):
        return self.string._iterator_()

    def _length_(self):
        return self.string._length_()

    def _at_index_(self, i):
        return self.string._at_index_(i)

    def _get_index_(self, obj):
        return self.string._get_index_(obj)

    def _at_(self, i):
        return self.string._at_index_(i)

    def _behavior_(self, process):
        return process.std.behaviors.Symbol


def string_or_symbol_string(var):
    if isinstance(var, W_String):
        return var
    if isinstance(var, W_Symbol):
        return var.string
    return None
