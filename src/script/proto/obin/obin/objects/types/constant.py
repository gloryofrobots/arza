from obin.objects import api
from root import W_Root


class W_Constant(W_Root):
    pass


class W_Undefined(W_Constant):
    _type_ = 'Undefined'

    def _tostring_(self):
        return "undefined"

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.UndefinedTraits



class W_Nil(W_Constant):
    _type_ = 'Nil'

    def _tostring_(self):
        return u'nil'

    def _tobool_(self):
        return False

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.NilTraits


class W_True(W_Constant):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def value(self):
        return True

    def _tostring_(self):
        return u'true'

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.TrueTraits

    def __str__(self):
        return '_True_'


class W_False(W_Constant):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def _tostring_(self):
        return u'false'

    def _tobool_(self):
        return False

    def value(self):
        return False

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.FalseTraits

    def __str__(self):
        return '_False_'