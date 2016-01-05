__author__ = 'gloryofrobots'
from root import W_Constant


class W_Boolean(W_Constant):
    pass


class W_True(W_Boolean):
    def _tostring_(self):
        return 'true'

    def _tobool_(self):
        return True

    def _behavior_(self, process):
        return process.std.behaviors.True

    def _hash_(self):
        return 1

    def __str__(self):
        return '_True_'


class W_False(W_Boolean):
    def _tostring_(self):
        return 'false'

    def _tobool_(self):
        return False

    def _behavior_(self, process):
        return process.std.behaviors.False

    def _hash_(self):
        return 0

    def __str__(self):
        return '_False_'
