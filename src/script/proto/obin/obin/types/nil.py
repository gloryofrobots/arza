from root import W_UniqueType

class W_Nil(W_UniqueType):
    def __init__(self):
        from obin.utils.misc import oid
        self.__hash = oid(self)

    def _tostring_(self):
        return 'nil'

    def _behavior_(self, process):
        return process.std.behaviors.Nil

    def _hash_(self):
        return self.__hash
