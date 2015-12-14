from root import W_Cell
from value import NativeListIterator
from obin.runtime.exception import *
from obin.objects import api


class W_Object(W_Cell):
    _type_ = 'Object'
    _immutable_fields_ = ['_type_']

    def __init__(self, slots):
        super(W_Object, self).__init__()
        from obin.objects.slots import newslots_empty

        if not slots:
            slots = newslots_empty()
        self.__slots = slots
        self.__traits = None
        self.__trait = None

    def has_traits(self):
        return self.__traits is not None

    def create_self_trait(self):
        from obin.objects.object_space import newtrait, newstring
        assert self.__traits
        assert not self.__trait
        self.__trait = newtrait(newstring(""))
        self.attach(self.__trait)

    def set_traits(self, traits):
        assert self.__traits is None
        self.__traits = traits

    # def __str__(self):
    #     return "W_Object(%s)" % (self._tostring_())

    def put_by_index(self, idx, value):
        self.__slots.set_by_index(idx, value)

    def get_by_index(self, idx):
        return self.__slots.get_by_index(idx)

    def get_index(self, name):
        return self.__slots.get_index(name)

    def traits(self):
        return self.__traits

    def has(self, k):
        from obin.objects.object_space import isundefined
        v = self._at_(k)
        return not isundefined(v)

    def _at_(self, k):
        from obin.objects.object_space import newundefined
        v = self.__slots.get(k)
        if v is None:
            return newundefined()

        return v

    def _lookup_(self, k):
        return self._at_(k)

    def _call_(self, routine, args):
        from obin.objects.object_space import newstring, isundefined
        cb = self._at_(newstring("__call__"))
        if isundefined(cb):
            raise ObinRuntimeError("Object is not callable")

        args.insert(0, self)
        return api.call(cb, routine, args)

    def _put_(self, k, v):
        if self.isfrozen():
            raise ObinRuntimeError("Object is frozen")
        self.__slots.add(k, v)

    def _iterator_(self):
        keys = self.__slots.keys()
        return NativeListIterator(keys, len(keys))

    def _tobool_(self):
        return True

    def _length_(self):
        return self.__slots.length()

    def _tostring_(self):
        from obin.objects.object_space import newstring, isundefined

        _name_ = self._at_(newstring("__name__"))
        if isundefined(_name_):
            return str(self.__slots)
        else:
            return "<object %s %s>" % (_name_._tostring_(), self.id())

    def _clone_(self):
        import copy
        slots = copy.copy(self.__slots)
        clone = W_Object(slots)
        traits = copy.copy(self.__traits)
        clone.set_traits(traits)
        return clone

    def _kindof_(self, trait):
        if self.traits().has(trait):
            return True

        return False

    def _traits_(self):
        return self.__traits

    def _totrait_(self):
        if not self.__trait:
            self.create_self_trait()
            # raise ObinRuntimeError(u"Can't convert object to trait")
        return self.__trait

    def attach(self, trait):
        from obin.objects.object_space import istrait
        assert self.__traits
        assert istrait(trait)
        self.traits().prepend(trait)

    def detach(self, trait):
        from obin.objects.object_space import istrait
        assert istrait(trait)
        try:
            self.traits().remove(trait)
        except KeyError:
            raise ObinTraitError(u"Detach trait error", trait)

    def get_trait_index(self, trait):
        return self.traits().get_index(trait)
