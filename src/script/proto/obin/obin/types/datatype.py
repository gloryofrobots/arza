from obin.types.root import W_Hashable
from obin.types import api, space, plist
from obin.misc import platform
from obin.runtime import error


class W_Record(W_Hashable):
    def __init__(self, type, descriptors, values):
        W_Hashable.__init__(self)
        self.descriptors = descriptors
        self.values = values
        self.type = type

    def _to_string_(self):
        from obin.types import api
        res = []
        for k, i in self.descriptors.items():
            v = api.at_index(self.values, i)
            res.append("%s = %s" % (api.to_s(k), api.to_s(v)))

        return "%s {%s}" % (api.to_s(self.type), ", ".join(res))

    def _at_(self, name):
        idx = api.lookup(self.descriptors, name, space.newnil())
        if space.isnil(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)
        return api.at(self.values, idx)

    def _at_index_(self, idx):
        # accessing protected method instead of api.at_index for avoiding multiple 0 < idx < length check
        return self.values._at_index_(idx)

    def _put_(self, name, value):
        idx = api.lookup(self.descriptors, name, space.newnil())
        if space.isnil(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)

        newvalues = api.put(self.values, name, value)
        return W_Record(self.descriptors, newvalues)

    def _length_(self):
        return api.length(self.values)


def descriptors(fields):
    d = space.newmap()
    for i in range(len(fields)):
        f = fields[i]
        d = api.put(d, f, space.newint(i))
    return d


# BOTH TYPE CONSTRUCTOR AND TYPE IN ONE CLASS
class W_DataType(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, fields, constructor):
        W_Hashable.__init__(self)
        self.name = name
        self.fields = fields
        self.descriptors = descriptors(self.fields)

        # parent types declared with union
        self.union = None

        self.ctor = constructor
        self.traits = plist.empty()

    def add_trait(self, trait):
        if self.is_type_constructor():
            return error.throw_2(error.Errors.TRAIT_ALREADY_IMPLEMENTED, trait,
                                 space.newstring(u"Cant implement trait for type constructor. Use type instead"))

        if self.implements(trait):
            return error.throw_1(error.Errors.TRAIT_ALREADY_IMPLEMENTED, trait)

        self.traits = plist.cons(trait, self.traits)

    def add_traits(self, traits):
        for trait in traits:
            self.add_trait(trait)

    def implements(self, trait):
        return plist.contains(self.traits, trait)

    def is_type_constructor(self):
        return self.union is not None

    def be_part_of_union(self, union):
        assert plist.is_empty(self.traits)
        assert self.union is None
        self.union = union

    def is_part_of_union(self, union):
        assert union is not None
        assert self.union is not None
        return api.equal_b(self.union, union)

    def create_record(self, env):
        undef = space.newnil()
        values = space.newlist([])
        for f in self.fields:
            v = api.lookup(env, f, undef)
            if space.isnil(v):
                error.throw_2(error.Errors.CONSTRUCTOR, space.newstring(u"Missing required field"), f)

            values = plist.cons(v, values)

        return W_Record(self, self.descriptors, values)

    # TODO CREATE CALLBACK OBJECT
    def _to_routine_(self, stack, args):
        from obin.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.create_record, self.ctor, args)
        return routine

    def _call_(self, process, args):
        process.call_object(self, args)

    def _type_(self, process):
        raise NotImplementedError()

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _equal_(self, other):
        return other is self


def can_coerce(_type, kind):
    if kind.is_type_constructor():
        return api.equal_b(_type, kind)

    if not _type.is_type_constructor():
        return api.equal_b(_type, kind)

    return _type.is_part_of_union(kind)

