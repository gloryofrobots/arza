from root import W_Constant

class W_Undefined(W_Constant):
    def __init__(self):
        from obin.utils.builtins import oid
        self.__hash = oid(self)

    def _tostring_(self):
        return "undefined"

    def _traits_(self, process):
        return process.stdlib.traits.UndefinedTraits

    def _hash_(self):
        return self.__hash

