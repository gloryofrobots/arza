from obin.objects.types.root import W_Hashable
from obin.objects import api
from obin.utils.builtins import random


class W_Trait(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name):
        W_Hashable.__init__(self)
        self._name_ = name

    def _compute_hash_(self):
        return int((1 - random()) * 10000000)

    def _totrait_(self, process):
        return self

    def _tostring_(self):
        return "<trait %s>" % (api.to_native_string(self._name_))

    def _equal_(self, other):
        return other is self
