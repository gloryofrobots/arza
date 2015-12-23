from obin.objects import api
from root import W_Root


class W_Constant(W_Root):
    pass


class W_Undefined(W_Constant):
    def _tostring_(self):
        return "undefined"

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.UndefinedTraits



class W_Nil(W_Constant):
    def _tostring_(self):
        return 'nil'

    def _tobool_(self):
        return False

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.NilTraits


class W_True(W_Constant):
    def _tostring_(self):
        return 'true'

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.TrueTraits

    def __str__(self):
        return '_True_'


class W_False(W_Constant):
    def _tostring_(self):
        return 'false'

    def _tobool_(self):
        return False

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.FalseTraits

    def __str__(self):
        return '_False_'
