__author__ = 'gloryofrobots'
import capy.types.root
from root import W_UniqueType


class W_Boolean(W_UniqueType):
    pass


class W_True(W_Boolean):
    def _to_string_(self):
        return 'True'

    def _to_repr_(self):
        return self._to_string_()

    def _to_bool_(self):
        return True

    def _type_(self, process):
        return process.std.classes.Bool

    def _hash_(self):
        return 1

    def __str__(self):
        return '_True_'


class W_False(W_Boolean):
    def _to_string_(self):
        return 'False'

    def _to_repr_(self):
        return self._to_string_()

    def _to_bool_(self):
        return False

    def _type_(self, process):
        return process.std.classes.Bool

    def _hash_(self):
        return 0

    def __str__(self):
        return '_False_'
