from obin.objects import api
from oroot import W_Root


class W_Constant(W_Root):
    pass


class W_Undefined(W_Constant):
    def __init__(self):
        from obin.utils.builtins import oid
        self.__hash = oid(self)

    def _tostring_(self):
        return "undefined"

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.UndefinedTraits

    def _hash_(self):
        return self.__hash


class W_Nil(W_Constant):
    def __init__(self):
        from obin.utils.builtins import oid
        self.__hash = oid(self)

    def _tostring_(self):
        return 'nil'

    def _tobool_(self):
        return False

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.NilTraits

    def _hash_(self):
        return self.__hash


class W_True(W_Constant):
    def _tostring_(self):
        return 'true'

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.TrueTraits

    def _hash_(self):
        return 1

    def __str__(self):
        return '_True_'


class W_False(W_Constant):
    def _tostring_(self):
        return 'false'

    def _tobool_(self):
        return False

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.FalseTraits

    def _hash_(self):
        return 0

    def __str__(self):
        return '_False_'
