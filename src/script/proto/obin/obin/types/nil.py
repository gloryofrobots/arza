from root import W_UniqueType
from obin.misc import platform
class W_Nil(W_UniqueType):
    def __init__(self):
        self.__hash = platform.obin_id(self)

    def _to_string_(self):
        return 'nil'

    def _type_(self, process):
        return process.std.types.Nil

    def _hash_(self):
        return self.__hash
