from lalan.types.root import W_Hashable
from lalan.types import api, space, plist
from lalan.misc import platform
from lalan.runtime import error


class W_Record(W_Hashable):
    def __init__(self, type, values):
        W_Hashable.__init__(self)
        self.values = values
        self.type = type

    def _dispatch_(self, process, generic):
        impl = self.type.get_method(generic)
        return impl

    def _to_string_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_s(f), api.to_s(v)))

        return "<%s (%s)>" % (api.to_s(self.type), ", ".join(res))

    def _to_repr_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_r(f), api.to_r(v)))

        return "<%s (%s)>" % (api.to_r(self.type), ", ".join(res))

    def _type_(self, process):
        return self.type

    def _at_(self, name):
        if space.isint(name):
            return self._at_index_(api.to_i(name))

        idx = api.lookup(self.type.descriptors, name, space.newvoid())
        if space.isvoid(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)
        return api.at(self.values, idx)

    def _contains_(self, key):
        value = self._at_(key)
        return not space.isvoid(value)

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
        self.interfaces = space.newmap()
        self.methods = space.newmap()
        self.derived_generics = plist.empty()

    def is_interface_implemented(self, iface):
        flag = api.lookup(self.interfaces, iface, space.newvoid())
        if space.isvoid(flag):
            accepted = iface.accept_type(self)
            api.put(self.interfaces, iface, space.newbool(accepted))
            return accepted
        else:
            return api.to_b(flag)

    def register_derived(self, generic):
        if self.is_derived(generic):
            return error.throw_3(error.Errors.RUNTIME_ERROR,
                                 space.newstring(u"Generic has already derived"), self, generic)

        self.derived_generics = plist.cons(generic, self.derived_generics)

    def is_derived(self, generic):
        if plist.contains(self.derived_generics, generic):
            return True
        return False

    def add_method(self, generic, method):
        error.affirm_type(generic, space.isgeneric)
        if self.is_generic_implemented(generic):
            if not self.is_derived(generic):
                return error.throw_3(error.Errors.IMPLEMENTATION_ERROR, self,
                                     space.newstring(u"Generic has already implemented"), generic)

            self.remove_method(generic)
        api.put(self.methods, generic, method)

    def add_methods(self, implementations):
        for impl in implementations:
            generic = api.at_index(impl, 0)
            error.affirm_type(generic, space.isgeneric)
            if self.is_generic_implemented(generic):
                if not self.is_derived(generic):
                    return error.throw_3(error.Errors.IMPLEMENTATION_ERROR, self,
                                         space.newstring(u"Generic has already implemented"), generic)

                self.remove_method(generic)

        for impl in implementations:
            generic = api.at_index(impl, 0)
            method = api.at_index(impl, 1)
            self.add_method(generic, method)

    def add_derived_methods(self, implementations):
        for impl in implementations:
            generic = api.at_index(impl, 0)
            method = api.at_index(impl, 1)

            self.register_derived(generic)
            self.add_method(generic, method)

    def is_generic_implemented(self, generic):
        return api.contains_b(self.methods, generic)

    def get_method(self, generic):
        return api.lookup(self.methods, generic, space.newvoid())

    def remove_method(self, generic):
        api.delete(self.methods, generic)


class W_DataType(W_Extendable):
    def __init__(self, name, fields):
        W_Extendable.__init__(self)

        self.name = name
        self.fields = fields
        self.arity = api.length_i(self.fields)

        if plist.is_empty(self.fields):
            self.is_singleton = True
        else:
            self.is_singleton = False

        self.descriptors = descriptors(self.fields)

    def _dispatch_(self, process, method):
        impl = space.newvoid()
        if self.is_singleton:
            impl = self.get_method(method)

        if space.isvoid(impl):
            _type = api.get_type(process, self)
            impl = _type.get_method(method)

        return impl

    def _call_(self, process, args):
        length = api.length_i(args)
        if length != self.arity:
            error.throw_4(error.Errors.CONSTRUCTOR_ERROR,
                          space.newstring(u"Invalid count of data for construction of type"),
                          self,
                          api.length(self.fields),
                          args)

        return W_Record(self, space.newpvector(args.to_l()))

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


def record_index_of(record, obj):
    error.affirm_type(record, space.isrecord)
    return record.index_of(obj)


def record_keys(record):
    error.affirm_type(record, space.isrecord)
    return record.keys()


def record_values(record):
    error.affirm_type(record, space.isrecord)
    return record.values()


def _is_exist_implementation(method, impl):
    impl_method = api.at_index(impl, 0)
    return api.equal_b(impl_method, method)


def newtype(process, name, fields):
    _datatype = W_DataType(name, fields)
    if process.std.initialized is False:
        return _datatype

    derive_default(process, _datatype)
    return _datatype


def _find_constraint_generic(generic, pair):
    return api.equal_b(pair[0], generic)


def _get_extension_methods(_type, _mixins, _methods):
    # BETTER WAY IS TO MAKE DATATYPE IMMUTABLE
    # AND CHECK CONSTRAINTS AFTER SETTING ALL METHO
    total = plist.empty()
    constraints = plist.empty()
    error.affirm_type(_methods, space.islist)
    for trait in _mixins:
        error.affirm_type(trait, space.istrait)
        constraints = plist.concat(constraints, trait.constraints)
        trait_methods = trait.to_list()
        total = plist.concat(trait_methods, total)

    total = plist.concat(_methods, total)

    for iface in constraints:
        for generic in iface.generics:

            if not plist.contains_with(total, generic,
                                       _find_constraint_generic):
                return error.throw_4(error.Errors.CONSTRAINT_ERROR,
                                    _type, iface, generic,
                                    space.newstring(
                                        u"Dissatisfied trait constraint"))

    result = plist.empty()
    for pair in total:
        generic = pair[0]
        if plist.contains_with(result, generic, _find_constraint_generic):
            continue

        result = plist.cons(pair, result)

    return plist.reverse(result)


def derive_default(process, _type):
    derived = process.std.derived.get_derived(_type)
    derive(_type, derived)


def derive(_type, derived):
    error.affirm_iterable(derived, space.istrait)
    error.affirm_type(_type, space.isextendable)

    methods = _get_extension_methods(_type, derived, plist.empty())
    _type.add_derived_methods(methods)
    return _type


def extend(_type, mixins, methods):
    error.affirm_type(_type, space.isextendable)

    methods = _get_extension_methods(_type, mixins, methods)
    _type.add_methods(methods)
    return _type
