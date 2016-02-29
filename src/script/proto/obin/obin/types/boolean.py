__author__ = 'gloryofrobots'
import obin.types.root
from root import W_UniqueType


class W_Boolean(W_UniqueType):
    pass


class W_True(W_Boolean):
    def _to_string_(self):
        return 'true'

    def _to_bool_(self):
        return True

    def _type_(self, process):
        return process.std.types.True

    def _hash_(self):
        return 1

    def __str__(self):
        return '_True_'


class W_False(W_Boolean):
    def _to_string_(self):
        return 'false'

    def _to_bool_(self):
        return False

    def _type_(self, process):
        return process.std.types.False

    def _hash_(self):
        return 0

    def __str__(self):
        return '_False_'
