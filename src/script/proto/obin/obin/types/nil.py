from root import W_UniqueType
from obin.misc import platform
class W_Nil(W_UniqueType):
    def __init__(self):
        self.__hash = platform.obin_id(self)

    def _to_string_(self):
        return 'nil'

    def _behavior_(self, process):
        return process.std.behaviors.Nil

    def _hash_(self):
        return self.__hash
