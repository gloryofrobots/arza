from root import W_Cell
from value import W_ValueType
from obin.runtime.exception import *
from obin.objects import api

class ObjectIterator(W_ValueType):
    def __init__(self, source, length):
        assert isinstance(source, list)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self.__source_length = length

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self.__source_length:
            return newundefined()

        el = self.source[self.index]
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.__source_length)

    def _tobool_(self):
        if self.index >= self.__source_length:
            return False
        return True

class W_Object(W_Cell):
    _type_ = 'Object'
    _immutable_fields_ = ['_type_']

    def __init__(self, slots):
        W_Cell.__init__(self)
        from obin.objects.slots import newslots_empty

        if not slots:
            slots = newslots_empty()
        self._slots = slots
        self._traits = None
        self._trait = None

    def has_traits(self):
        return self._traits is not None

    def create_self_trait(self):
        from obin.objects.space import newtrait, newstring
        assert self._traits
        assert not self._trait
        self._trait = newtrait(newstring(u""))
        self.attach(self._trait)

    def set_traits(self, traits):
        assert self._traits is None
        self._traits = traits

    # def __str__(self):
    #     return "W_Object(%s)" % (self._tostring_())

    def put_by_index(self, idx, value):
        self._slots.set_by_index(idx, value)

    def get_by_index(self, idx):
        return self._slots.get_by_index(idx)

    def get_index(self, name):
        return self._slots.get_index(name)

    def traits(self):
        return self._traits

    def has(self, k):
        from obin.objects.space import isundefined
        v = self._at_(k)
        return not isundefined(v)

    def _at_(self, k):
        from obin.objects.space import newundefined
        v = self._slots.get(k)
        if v == -1000:
            return newundefined()

        return v

    def _lookup_(self, k):
        return self._at_(k)

    def _call_(self, routine, args):
        from obin.objects.space import newstring, isundefined
        cb = self._at_(newstring(u"__call__"))
        if isundefined(cb):
            raise ObinRuntimeError(u"Object is not callable")

        args.insert(0, self)
        return api.call(cb, routine, args)

    def _put_(self, k, v):
        if self.isfrozen():
            raise ObinRuntimeError(u"Object is frozen")
        self._slots.add(k, v)

    def _iterator_(self):
        keys = self._slots.keys()
        return ObjectIterator(keys, len(keys))

    def _tobool_(self):
        return True

    def _length_(self):
        return self._slots.length()

    def _tostring_(self):
        return str("{%s %s}" % (str(self._slots), str(self._traits)))

    def _clone_(self):
        slots = self._slots.copy()
        clone = W_Object(slots)
        traits = self._traits.copy()
        clone.set_traits(traits)
        return clone

    def _kindof_(self, trait):
        if self.traits().has(trait):
            return True

        return False

    def _traits_(self):
        return self._traits

    def _totrait_(self):
        if not self._trait:
            self.create_self_trait()
        return self._trait

    def attach(self, trait):
        from obin.objects.space import istrait
        assert self._traits
        assert istrait(trait)
        self.traits().prepend(trait)

    def detach(self, trait):
        from obin.objects.space import istrait
        assert istrait(trait)
        try:
            self.traits().remove(trait)
        except KeyError:
            raise ObinTraitError(u"Detach trait error", trait)

