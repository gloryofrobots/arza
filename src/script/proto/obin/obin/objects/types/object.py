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

        self.__origin = None
        self.__traits = None

    def has_traits(self):
        return self.__traits is not None

    def create_traits(self, traits):
        from obin.objects.object_space import newvector
        assert self.traits() is None
        if not traits:
            traits = newvector()

        self.__traits = traits

    def set_origin(self, origin):
        self.origin = origin

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

    def _lookup_(self, k):
        from obin.objects.object_space import isundefined, newundefined
        v = self._at_(k)
        if not isundefined(v):
            return v

        for t in self.traits().values():
            v = t._at_(k)
            if not isundefined(v):
                return v

        return newundefined()

    def _at_(self, k):
        from obin.objects.object_space import newundefined
        v = self.__slots.get(k)
        if v is None:
            return newundefined()

        return v

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
        clone.create_traits(traits)
        return clone

    def kindof(self, obj2):
        from obin.objects.object_space import isobject
        assert isobject(obj2)
        if self is obj2:
            return True

        if obj2 is self.origin:
            return True

        if self.traits().has(obj2):
            return True

        if not self.origin:
            return False

        return self.origin.kindof(obj2)


    def add_trait(self, trait):
        from obin.objects.object_space import istrait
        assert istrait(trait)

        traits = self.traits()
        if not traits:
            self.create_traits(None)
            traits = self.traits()

        traits.prepend(trait)

    def remove_trait(self, trait):
        from obin.objects.object_space import istrait
        assert istrait(trait)
        try:
            self.traits().remove(trait)
        except KeyError:
            pass


