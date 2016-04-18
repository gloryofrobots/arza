from obin.types.root import W_Hashable
from obin.types import api, space, plist, pmap
from obin.misc import platform
from obin.runtime import error


class W_Record(W_Hashable):
    def __init__(self, type, values):
        W_Hashable.__init__(self)
        self.values = values
        self.type = type

    def _dispatch_(self, process, method):
        impl = self.type.get_method_implementation(method)
        if space.isvoid(impl) and self.type.union is not None:
            impl = self.type.union.get_method_implementation(method)

        return impl

    def _to_string_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_s(f), api.to_s(v)))

        return "%s {%s}" % (api.to_s(self.type), ", ".join(res))

    def _to_repr_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_r(f), api.to_r(v)))

        return "%s {%s}" % (api.to_r(self.type), ", ".join(res))

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


class W_Extendable(W_Hashable):
    def __init__(self):
        W_Hashable.__init__(self)
        from obin.builtins.derived import Derive
        self.derive = Derive()
        self.derived_traits = plist.empty()
        self.traits = space.newmap()

    def register_derived(self, trait):
        if self.is_derived(trait):
            return error.throw_3(error.Errors.TRAIT_ALREADY_IMPLEMENTED_ERROR,
                                 space.newstring(u"Trait has already derived"), self, trait)

        self.derived_traits = plist.cons(trait, self.derived_traits)

    def is_derived(self, trait):
        if plist.contains(self.derived_traits, trait):
            return True
        return False

    def remove_trait_implementation(self, trait):
        api.delete(self.traits, trait)

    def add_trait_implementation(self, trait, implementations):
        if self.is_trait_implemented(trait):
            if not self.is_derived(trait):
                return error.throw_2(error.Errors.TRAIT_ALREADY_IMPLEMENTED_ERROR, self, trait)
            self.remove_trait_implementation(trait)

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

        impl = api.lookup(impl_map, method, void)
        if space.isvoid(impl):
            error.throw_4(error.Errors.METHOD_INVOKE_ERROR, space.newstring(u"Invalid dispatch."
                                                                            u"Method does not belong to trait"),
                          trait, method, impl_map)

        return impl


class W_DataType(W_Extendable):
    def __init__(self, name, fields, constructor):
        W_Extendable.__init__(self)

        self.name = name
        self.fields = fields

        if plist.is_empty(self.fields):
            self.is_singleton = True
        else:
            self.is_singleton = False

        self.descriptors = descriptors(self.fields)
        self.ctor = constructor
        self.union = None

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

        return W_Record(self, space.newpvector(values))
        # return W_Record(self, plist.plist(values))

    def _dispatch_(self, process, method):
        impl = space.newvoid()
        if self.union is not None:
            impl = self.union.get_method_implementation(method)

        if space.isvoid(impl):
            _type = api.get_type(process, self)
            impl = _type.get_method_implementation(method)

        return impl

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

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


class W_Union(W_Extendable):
    def __init__(self, name, types):
        W_Extendable.__init__(self)
        self.name = name
        self.types_list = types
        self.types_map = space.newpmap([])
        for _t in self.types_list:
            self.types_map = api.put(self.types_map, _t.name, _t)

        self.length = api.length_i(self.types_list)

    def _at_(self, key):
        return api.at(self.types_map, key)

    def _length_(self):
        return self.length

    def has_type(self, _type):
        return plist.contains(self.types_list, _type)

    def _dispatch_(self, process, method):
        # print "UNION DISPATCH", method
        impl = self.get_method_implementation(method)
        # print "UNION IMPL1", impl
        if space.isvoid(impl):
            _type = self._type_(process)
            impl = _type.get_method_implementation(method)
            # print "UNION IMPL2", impl
        return impl

    def _type_(self, process):
        return process.std.types.Union

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return "<type %s>" % api.to_s(self.name)

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self

    def to_list(self):
        return self.types_list


def union_to_list(union):
    error.affirm_type(union, space.isunion)
    return union.to_list()


def get_union(process, w):
    if not space.isdatatype(w):
        _t = api.get_type(process, w)
    else:
        _t = w

    if _t.union is not None:
        return _t.union
    return error.throw_2(error.Errors.TYPE_ERROR, space.newstring(u"Type is not part of any union"), _t)


def _is_exist_implementation(method, impl):
    impl_method = api.at_index(impl, 0)
    return api.equal_b(impl_method, method)


def newtype(process, name, fields, constructor):
    _datatype = W_DataType(name, fields, constructor)
    if process.std.initialized is False:
        return _datatype

    derive_default(process, _datatype)
    return _datatype


def newunion(process, name, types):
    error.affirm_type(name, space.issymbol)
    error.affirm_type(types, space.islist)
    for _t in types:
        if _t.union is not None:
            return error.throw_3(error.Errors.TYPE_ERROR, _t, _t.union,
                                 space.newstring(u"Type already exists in union"))
    _union = W_Union(name, types)
    for _t in types:
        _t.union = _union

    if process.std.initialized is False:
        return _union
    derive_default(process, _union)
    return _union


def derive_default(process, _type):
    if space.isdatatype(_type):
        if _type.is_singleton:
            traits = process.std.traits.derive_default_singleton(_type)
        else:
            traits = process.std.traits.derive_default_record(_type)
        for _t, _i in traits:
            _implement_trait(_type, _t, _i)
            _type.register_derived(_t)
    elif space.isunion(_type):
        traits = process.std.traits.derive_default_union(_type)
        for _t, _i in traits:
            methods = _normalise_implementations(_t, _i)
            _implement_trait(_type, _t, methods)
            _type.register_derived(_t)
    else:
        return error.throw_2(error.Errors.TYPE_ERROR, space.newstring(u"Type or Union Expected"), _type)


def extend_type(_type, traits):
    for trait_data in traits:
        trait = trait_data[0]
        impls = trait_data[1]
        implement_trait(_type, trait, impls)
    return _type


def _normalise_implementations(trait, implementations):
    if space.ispmap(implementations):
        methods = plist.empty()
        for method in trait.methods:
            impl = api.lookup(implementations, method.name, space.newvoid())
            if not space.isvoid(impl):
                methods = plist.cons(space.newtuple([method.name, impl]), methods)
    elif space.isextendable(implementations):
        methods = plist.empty()
        for method in trait.methods:
            impl = implementations.get_method_implementation(method)
            methods = plist.cons(space.newtuple([method.name, impl]), methods)
    elif space.islist(implementations):
        methods = implementations
    else:
        return error.throw_2(error.Errors.TYPE_ERROR,
                             space.newstring(u"Invalid trait implementation source. Expected one of Map,List,Type"),
                             implementations)
    method_impls = plist.empty()
    # Collect methods by names from trait
    for im in methods:
        method_name = api.at_index(im, 0)
        fn = api.at_index(im, 1)
        error.affirm_type(fn, space.isfunction)
        method = trait.find_method_by_name(method_name)
        if space.isvoid(method):
            error.throw_2(error.Errors.TRAIT_IMPLEMENTATION_ERROR,
                          space.newstring(u"Unknown method"), method_name)
        method_impls = plist.cons(space.newlist([method, fn]), method_impls)
    return method_impls


def implement_trait(_type, trait, implementations):
    error.affirm_type(_type, space.isextendable)
    error.affirm_type(trait, space.istrait)
    methods = _normalise_implementations(trait, implementations)
    return _implement_trait(_type, trait, methods)


def _implement_trait(_type, trait, method_impls):
    error.affirm_type(_type, space.isextendable)
    error.affirm_type(trait, space.istrait)
    error.affirm_type(method_impls, space.islist)
    # print "IMPLEMENT ", _type, trait
    for constraint in trait.constraints:
        if not _type.is_trait_implemented(constraint):
            error.throw_3(error.Errors.TRAIT_CONSTRAINT_ERROR,
                          space.newstring(u"Unsatisfied trait constraint"), trait, constraint)
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
