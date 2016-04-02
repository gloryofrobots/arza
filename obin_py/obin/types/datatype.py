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

        idx = api.lookup(self.type.descriptors, name, space.newvoid())
        if space.isvoid(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)
        return api.at(self.values, idx)

    def _at_index_(self, idx):
        # accessing protected method instead of api.at_index for avoiding multiple 0 < idx < length check
        return self.values._at_index_(idx)

    def _put_(self, name, value):
        idx = api.lookup(self.type.descriptors, name, space.newvoid())
        if space.isvoid(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)

        newvalues = api.put(self.values, name, value)
        return W_Record(self.type.descriptors, newvalues)

    def _length_(self):
        return api.length(self.values)

    def _equal_(self, other):
        if not isinstance(other, W_Record):
            return False
        if not api.equal_b(self.type, other.type):
            return False
        return api.equal_b(self.values, other.values)

    def seq(self):
        return self.values

    def keys(self):
        return self.type.fields

    def values(self):
        return self.values

    def index_of(self, val):
        idx = self.values.index(val)
        if platform.is_absent_index(idx):
            error.throw_1(error.Errors.VALUE_ERROR, val)
        return idx


def descriptors(fields):
    d = space.newmap()
    for i in range(len(fields)):
        f = fields[i]
        d = api.put(d, f, space.newint(i))
    return d


class W_DataType(W_Hashable):
    def __init__(self, name, fields, constructor):
        from obin.builtins.derived import Derive
        W_Hashable.__init__(self)

        self.name = name
        self.fields = fields
        self.descriptors = descriptors(self.fields)
        self.ctor = constructor
        self.derive = Derive()
        self.traits = space.newmap()

    def add_trait_implementation(self, trait, implementations):
        if self.is_trait_implemented(trait):
            return error.throw_1(error.Errors.TRAIT_ALREADY_IMPLEMENTED_ERROR, trait)

        impl_map = space.newmap()
        for impl in implementations:
            method = api.at_index(impl, 0)
            func = api.at_index(impl, 1)
            api.put(impl_map, method, func)

        api.put(self.traits, trait, impl_map)

    def is_trait_implemented(self, trait):
        return api.contains_b(self.traits, trait)

    def get_method_implementation(self, method):
        void = space.newvoid()
        trait = method.trait

        impl_map = api.lookup(self.traits, trait, void)
        if impl_map is void:
            return void

        impl = api.at(impl_map, method)
        return impl

    def has_constructor(self):
        return not space.isvoid(self.ctor)

    def create_instance(self, env):
        undef = space.newvoid()
        values = []

        for f in self.fields:
            v = api.lookup(env, f, undef)
            if space.isvoid(v):
                error.throw_2(error.Errors.CONSTRUCTOR_ERROR,
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
            error.throw_2(error.Errors.CONSTRUCTOR_ERROR,
                          space.newstring(u"There are no constructor for type"), self)

        process.call_object(self, args)

    def _type_(self, process):
        return process.std.types.Datatype

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _equal_(self, other):
        return other is self

class W_Union(W_Hashable):
    def __init__(self, name, types):
        W_Hashable.__init__(self)
        self.name = name
        self.types = types

    def has_type(self, _type):
        return plist.contains(self.types, _type)

    def _type_(self, process):
        return process.std.types.Datatype

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return "<type %s>" % api.to_s(self.name)

    def _equal_(self, other):
        return other is self


def _is_exist_implementation(method, impl):
    impl_method = api.at_index(impl, 0)
    return api.equal_b(impl_method, method)


def derive_traits(process, _type, traits):
    if space.isunion(_type):
        for t in _type.types:
            derive_traits(process, t, traits)

    error.affirm_type(_type, space.isdatatype)

    for trait in traits:
        error.affirm_type(trait, space.istrait)
        if _type.is_trait_implemented(trait):
            return error.throw_3(error.Errors.TRAIT_IMPLEMENTATION_ERROR, trait, _type,
                                 space.newstring(u"Trait already implemented"))

        # more then one trait can be returned
        # example deriving Dict causes deriving Collection
        implementations = process.std.traits.derive(_type, trait)
        for _t, _i in implementations:
            _implement_trait(_type, _t, _i)


def implement_trait(_type, trait, implementations):
    if space.isunion(_type):
        for t in _type.types:
            implement_trait(t, trait, implementations)

    error.affirm_type(_type, space.isdatatype)
    error.affirm_type(trait, space.istrait)
    error.affirm_type(implementations, space.islist)
    method_impls = plist.empty()
    # Collect methods by names from trait
    for im in implementations:
        method_name = api.at_index(im, 0)
        fn = api.at_index(im, 1)
        method = trait.find_method_by_name(method_name)
        if space.isvoid(method):
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION_ERROR,
                          space.newstring(u"Unknown method"), method_name)
        method_impls = plist.cons(space.newlist([method, fn]), method_impls)
    return _implement_trait(_type, trait, method_impls)


def _implement_trait(_type, trait, method_impls):
    error.affirm_type(_type, space.isdatatype)
    error.affirm_type(trait, space.istrait)
    error.affirm_type(method_impls, space.islist)
    for constraint in trait.constraints:
        if not _type.is_trait_implemented(constraint):
            error.throw_2(error.Errors.TRAIT_CONSTRAINT_ERROR,
                          space.newstring(u"Unsatisfied trait constraint"), constraint)
    # GET DEFAULTS FIRST
    for m in trait.methods:
        if plist.contains_with(method_impls, m, _is_exist_implementation):
            continue

        if not m.has_default_implementation():
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION_ERROR,
                          space.newstring(u"Expected implementation of method"), m)

        method_impls = plist.cons(space.newlist([m, m.default_implementation]),
                                  method_impls)

    for impl in method_impls:
        method = api.at_index(impl, 0)
        if not trait.has_method(method):
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION_ERROR, space.newstring(u"Unknown trait method"), method)
    _type.add_trait_implementation(trait, method_impls)
    return _type
