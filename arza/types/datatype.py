from arza.types.root import W_Hashable
from arza.types import api, space, plist
from arza.misc import platform
from arza.runtime import error


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


class MRO:
    def __init__(self):
        self.items = plist.empty()
        self.interfaces_index = 0

    def add_interface(self, interface):
        self.items = plist.insert(self.items, self.interfaces_index, interface)

    def add_type(self, type):
        self.items = plist.cons(type, self.items)
        self.interfaces_index += 1

    def weight(self, item):
        return plist.index(self.items, item)

    def has_type(self, type):
        return plist.contains(plist.take(self.items, self.interfaces_index), type)

    def has_interface(self, type):
        return plist.contains(plist.drop(self.items, self.interfaces_index), type)


class W_BaseDatatype(W_Hashable):
    def __init__(self, name, interfaces):
        W_Hashable.__init__(self)
        self.interfaces = interfaces
        self.mro = MRO()
        self.name = name

    def _register_interface(self, iface):
        if self.is_interface_implemented(iface):
            error.throw_3(error.Errors.IMPLEMENTATION_ERROR, space.newstring(u"Interface has already implemented"),
                          self, iface)

        self.interfaces = plist.cons(iface, self.interfaces)
        self.mro.add_interface(iface)
        iface.register_type(self)

    def register_interface(self, iface):
        for sub in iface.sub_interfaces:
            if not self.is_interface_implemented(sub):
                self._register_interface(sub)
        self._register_interface(iface)

    def is_interface_implemented(self, iface):
        return plist.contains(self.interfaces, iface)

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self


class W_NativeDatatype(W_BaseDatatype):
    def __init__(self, name):
        W_BaseDatatype.__init__(self, name, plist.empty())

    def _type_(self, process):
        return process.std.types.Datatype

    def _to_string_(self):
        return "<datatype %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()


class W_SingletonType(W_BaseDatatype):
    def __init__(self, name):
        W_BaseDatatype.__init__(self, name, plist.empty())

    def _type_(self, process):
        return process.std.types.Datatype

    def _to_string_(self):
        return "<SingletonDatatype %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return api.to_s(self.name)


class W_DataType(W_BaseDatatype):
    def __init__(self, name, fields):
        W_BaseDatatype.__init__(self, name, plist.empty())
        self.fields = fields
        self.arity = api.length_i(self.fields)
        self.descriptors = descriptors(self.fields)

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

    def _to_string_(self):
        return "<datatype %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()


def record_index_of(record, obj):
    error.affirm_type(record, space.isrecord)
    return record.index_of(obj)


def record_keys(record):
    error.affirm_type(record, space.isrecord)
    return record.keys()


def record_values(record):
    error.affirm_type(record, space.isrecord)
    return record.values()


def derive(process, t, interfaces):
    error.affirm_type(t, space.isdatatype)
    error.affirm_type(interfaces, space.islist)
    to_be_implemented = []

    old_interfaces = t.interfaces
    for interface in interfaces:
        if t.is_interface_implemented(interface):
            if process.std.interfaces.is_default_derivable_interface(interface):
                continue
            else:
                return error.throw_3(
                    error.Errors.IMPLEMENTATION_ERROR,
                    space.newstring(u"Interface already implemented"),
                    t,
                    interface
                )

        # derive according to future interfaces
        new_interfaces = plist.remove(interfaces, interface)
        maybe_interfaces = plist.concat(old_interfaces, new_interfaces)

        error.affirm_type(interface, space.isinterface)
        for r in interface.generics:
            generic = api.first(r)
            position = api.second(r)
            idx = api.to_i(position)
            if not generic.is_implemented_for_type(t, maybe_interfaces, idx):
                error.throw_5(
                    error.Errors.IMPLEMENTATION_ERROR,
                    space.newstring(u"Not implemented interface method"),
                    t,
                    interface,
                    generic,
                    position
                )

        to_be_implemented.append(interface)

    for interface in to_be_implemented:
        t.register_interface(interface)


def newnativedatatype(name):
    return W_NativeDatatype(name)


def newtype(process, name, fields):
    if plist.is_empty(fields):
        _type = W_SingletonType(name)
        _iface = process.std.interfaces.Singleton
    else:
        _type = W_DataType(name, fields)
        _iface = process.std.interfaces.Instance

    _type.register_interface(process.std.interfaces.Any)
    _type.register_interface(_iface)

    if process.std.initialized:
        derived = process.std.interfaces.get_derived(_type)
        derive(process, _type, derived)
    return _type