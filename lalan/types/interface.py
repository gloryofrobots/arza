from lalan.types.root import W_Hashable
from lalan.types import api, space, plist
from lalan.misc import platform
from lalan.runtime import error


def find_by_name(name, generic):
    return api.equal_b(generic.name, name)


class W_Interface(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, generics):
        W_Hashable.__init__(self)
        self.name = name
        self.generics = generics

    def find_generic_by_name(self, name):
        return plist.find_with(self.generics, name, find_by_name)

    def has_generic_name(self, name):
        return not space.isvoid(plist.find_with(self.generics, name, find_by_name))

    def _at_(self, key):
        return plist.find_with(self.generics, key, find_by_name)

    def accept_type(self, _type):
        for generic in self.generics:
            if not _type.is_generic_implemented(generic):
                return False
        return True

    # def add_generic(self, method):
    #     assert space.isgeneric(method)
    #     self.generics = plist.cons(method, self.generics)

    def has_generic(self, method):
        return plist.contains(self.generics, method)

    def _type_(self, process):
        return process.std.types.Interface

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


def _get_mixin_generics(generics, mixins):
    for pair in mixins:
        iface = api.at_index(pair, 0)
        error.affirm_type(iface, space.isinterface)
        gen_names = api.at_index(pair, 1)
        if space.isvoid(gen_names):
            generics = plist.concat(generics, iface.generics)
        else:
            for gen_name in gen_names:
                gen = iface.find_generic_by_name(gen_name)
                if space.isvoid(gen):
                    return error.throw_3(error.Errors.METHOD_SPECIALIZE_ERROR,
                                         iface, gen_name,
                                         space.newstring(
                                             u"Interface does not have this generic"))
                generics = plist.cons(gen, generics)

    return generics


def newinterface(name, generics, mixins):
    if not space.isvoid(mixins):
        generics = _get_mixin_generics(generics, mixins)
    return W_Interface(name, generics)
