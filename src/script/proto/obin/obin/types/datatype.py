from obin.types.root import W_Hashable
from obin.types import api, space, plist, pmap
from obin.misc import platform
from obin.runtime import error


class W_Record(W_Hashable):
    def __init__(self, type, values):
        W_Hashable.__init__(self)
        self.values = values
        self.type = type

    def _to_string_(self):
        from obin.types import api
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_s(f), api.to_s(v)))

        return "%s {%s}" % (api.to_s(self.type), ", ".join(res))

    def _type_(self, process):
        return self.type

    def _at_(self, name):
        if space.isint(name):
            return self._at_index_(api.to_i(name))

        idx = api.lookup(self.type.descriptors, name, space.newnil())
        if space.isnil(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)
        return api.at(self.values, idx)

    def _at_index_(self, idx):
        # accessing protected method instead of api.at_index for avoiding multiple 0 < idx < length check
        return self.values._at_index_(idx)

    def _put_(self, name, value):
        idx = api.lookup(self.type.descriptors, name, space.newnil())
        if space.isnil(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)

        newvalues = api.put(self.values, name, value)
        return W_Record(self.type.descriptors, newvalues)

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
        self.ctor = constructor

        # parent types declared with union
        self.union = None
        # if union is set traits must be empty
        self.traits = space.newmap()

    def add_trait_implementation(self, trait, implementations):
        if self.is_part_of_some_union():
            return error.throw_2(error.Errors.TYPE, trait,
                                 space.newstring(u"Can't implement trait for type constructor. Use type instead"))

        if self.is_trait_implemented(trait):
            return error.throw_1(error.Errors.TRAIT_ALREADY_IMPLEMENTED, trait)

        impl_map = space.newmap()
        for impl in implementations:
            method = api.at_index(impl, 0)
            func = api.at_index(impl, 1)
            api.put(impl_map, method, func)

        api.put(self.traits, trait, impl_map)

    def is_trait_implemented(self, trait):
        return api.contains_b(self.traits, trait)

    def get_method_implementation(self, method):
        void = space.newnil()
        if self.is_part_of_some_union():
            return void

        trait = method.trait

        impl_map = api.lookup(self.traits, trait, void)
        if impl_map is void:
            return void

        impl = api.at(impl_map, method)
        return impl

    def is_part_of_some_union(self):
        return self.union is not None

    def be_part_of(self, union):
        assert api.is_empty(self.traits)
        assert self.union is None
        self.union = union

    def is_part_of(self, union):
        assert union is not None
        assert self.union is not None
        return api.equal_b(self.union, union)

    def has_constructor(self):
        return not space.isnil(self.ctor)

    def create_instance(self, env):
        undef = space.newnil()
        values = []

        for f in self.fields:
            v = api.lookup(env, f, undef)
            if space.isnil(v):
                error.throw_2(error.Errors.CONSTRUCTOR,
                              space.newstring(u"Missing required field. Check recursive constructor call"), f)
            values.append(v)

        return W_Record(self, plist.plist(values))

    # TODO CREATE CALLBACK OBJECT
    def _to_routine_(self, stack, args):
        from obin.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.create_instance, self.ctor, args)
        return routine

    def _call_(self, process, args):
        if not self.has_constructor():
            error.throw_2(error.Errors.CONSTRUCTOR,
                          space.newstring(u"Type is not constructor"), self)

        process.call_object(self, args)

    def _type_(self, process):
        if self.union:
            return self.union

        return process.std.types.Datatype

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _equal_(self, other):
        return other is self


def _is_exist_implementation(method, impl):
    impl_method = api.at_index(impl, 0)
    return api.equal_b(impl_method, method)


def implement_trait(_type, trait, implementations):
    error.affirm_type(_type, space.isdatatype)
    error.affirm_type(trait, space.istrait)
    error.affirm_type(implementations, space.islist)
    # GET DEFAULTS FIRST
    for m in trait.methods:
        if plist.contains_with(implementations, m, _is_exist_implementation):
            continue

        if not m.has_default_implementation():
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION,
                          space.newstring(u"Expected implementation of method"), m)

        implementations = plist.cons(plist.plist([m, m.default_implementation]),
                                     implementations)

    for impl in implementations:
        method = api.at_index(impl, 0)
        if not trait.has_method(method):
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION, space.newstring(u"Unknown trait method"), method)
    _type.add_trait_implementation(trait, implementations)
    return _type


def newunion(union, types):
    error.affirm_type(union, space.isdatatype)
    error.affirm_type(types, space.islist)
    for _type in types:
        error.affirm_type(_type, space.isdatatype)
        _type.be_part_of(union)

    return union


def can_coerce(_type, kind):
    if kind.is_part_of_some_union():
        return api.equal_b(_type, kind)

    if not _type.is_part_of_some_union():
        return api.equal_b(_type, kind)

    return _type.is_part_of(kind)
