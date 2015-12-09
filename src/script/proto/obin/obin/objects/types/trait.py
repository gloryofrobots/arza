from root import W_Cell
from obin.runtime.exception import *
from obin.objects import api


class W_Trait(W_Cell):
    _type_ = 'Trait'
    _immutable_fields_ = ['_type_']

    def __init__(self, slots):
        super(W_Cell, self).__init__()
        from obin.objects.slots import newvector
        self.__methods = newvector()

    def _register_(self, method, signature):
        length = signature.length()
        methods = self.__methods
        methods.ensure_size(length)
        index = length - 1




