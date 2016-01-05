from root import W_Constant

class W_Nil(W_Constant):
    def __init__(self):
        from obin.utils.misc import oid
        self.__hash = oid(self)

    def _tostring_(self):
        return 'nil'

    def _tobool_(self):
        return False

    def _behavior_(self, process):
        return process.std.behaviors.Nil

    def _hash_(self):
        return self.__hash
