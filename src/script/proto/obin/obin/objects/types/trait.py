from root import W_Cell
from obin.runtime.exception import *
from obin.objects import api
from rpython.rlib.rrandom import Random
r = Random()

class W_Trait(W_Cell):
    _type_ = 'Trait'
    _immutable_fields_ = ['_type_']

    def __init__(self, name):
        self._name_ = name
        v = r.random()
        _id = (1 - v)
        _id = _id * 10000000
        __id = int(_id)
        # __id2 = id(self)
        # print "Trait", __id, __id2
        self.__id = __id

    def _totrait_(self):
        return self

    def _tostring_(self):
        return "<trait %s>" % (api.to_native_string(self._name_))

    def _hash_(self):
        return self.__id

    def _equal_(self, other):
        return other is self
