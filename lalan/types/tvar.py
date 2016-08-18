from lalan.types import api, space
from lalan.types.root import W_Root
from lalan.runtime import error


# TODO STM

class W_TVar(W_Root):
    def __init__(self, value):
        self.value = value

    def _to_string_(self):
        return "TVar(%s)" % api.to_s(self.value)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.TVar

    def _equal_(self, other):
        return self is other

def read(var):
    return var.value


def swap(var, value):
    var.value = value
