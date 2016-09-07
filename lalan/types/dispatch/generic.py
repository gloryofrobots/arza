from lalan.types.root import W_Hashable
from lalan.misc import platform
from lalan.builtins.hotpath import HotPath
from lalan.runtime import error
from lalan.types import api, space, plist, tuples
from signature import newsignature
from dag import *


def _dict_key(obj1, obj2):
    assert space.isany(obj1)
    assert space.isany(obj2)
    v = obj1._equal_(obj2)
    return v


def _dict_hash(obj1):
    assert space.isany(obj1)
    return obj1._hash_()


# TODO REMOVE IT
def group_dict():
    from lalan.misc.platform import r_dict
    return r_dict(_dict_key, _dict_hash)


class W_Generic(W_Hashable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, arity, dispatch_indexes, args_signature, hotpath):
        W_Hashable.__init__(self)

        self.name = name
        self.arity = arity
        self.dispatch_indexes = dispatch_indexes
        self.interfaces = plist.empty()
        self.arity = api.length_i(args_signature)
        self.dispatch_arity = len(dispatch_indexes)
        self.args_signature = args_signature
        self.signatures = []
        self.hot_path = hotpath
        self.count_call = 0
        self.dag = None

    def register_interface(self, interface, position):
        self.interfaces = plist.cons(space.newtuple([interface, position]), self.interfaces)

    def set_hotpath(self, hotpath):
        self.hot_path = HotPath(hotpath, self.arity)

    def _to_string_(self):
        return "<generic %s %s>" % (api.to_s(self.name), api.to_s(self.args_signature))

    def _to_repr_(self):
        return self._to_string_()

    def _call_(self, process, args):
        arity = api.length_i(args)
        if arity != self.arity:
            return error.throw_5(error.Errors.INVALID_ARG_COUNT_ERROR,
                                 space.newstring(u"Invalid count of arguments "),
                                 self, args, space.newint(arity), space.newint(self.arity))

        if self.hot_path is not None:
            res = self.hot_path.apply(process, args)
            if res is not None:
                return res

        dispatch_args = space.newtuple([args[i] for i in self.dispatch_indexes])

        method = self.dag.evaluate(process, dispatch_args)
        # print "GEN CALL", str(method)
        # method = lookup_implementation(process, self, args)
        assert method is not self

        # if space.isvoid(method):
        if not method:
            return error.throw_3(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR,
                                 self,
                                 space.newlist(self.signatures),
                                 args)

        # print "METHOD CALL", method, args
        process.call_object(method, args)

    def _type_(self, process):
        return process.std.types.Generic

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def add_signature(self, signature):
        self.signatures.append(signature)
        discriminators = []
        nodes = self._make_nodes(0, self.dispatch_arity, self.signatures, discriminators)
        self.dag = RootNode(nodes, discriminators)

    def _make_nodes(self, index, arity, signatures, discriminators):
        if index == arity:
            leaf = self._make_method_node(signatures)
            # print "METHOD", index, leaf
            return leaf

        groups = group_dict()
        # groups = space.newmap()
        for signature in signatures:
            arg = signature.get_argument(index)
            if arg not in groups:
                groups[arg] = [signature]
            else:
                groups[arg].append(signature)

        nodes = []
        for arg, group in groups.items():
            d = arg.discriminator(discriminators)
            children = self._make_nodes(index + 1, arity, group, discriminators)
            if len(children) == 1:
                nodes.append(SingleNode(d, children[0]))
            else:
                nodes.append(GroupNode(d, children))

        # print "NODES", index, nodes
        return nodes

    def _make_method_node(self, signatures):
        if len(signatures) != 1:
            return error.throw_3(error.Errors.METHOD_SPECIALIZE_ERROR,
                                 self,
                                 space.newlist(signatures),
                                 space.newstring(u"Ambiguous generic specialisation"))

        sig = signatures[0]
        return [LeafNode(sig.method)]


def specify(process, gf, types, method):
    if gf.dispatch_arity != api.length_i(types):
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Generic function arity inconsistent with specialisation arguments"))
    if gf.arity != method.arity:
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Bad method for specialisation, inconsistent arity"))

    gf.add_signature(newsignature(process, types, method))
    for index, _type in zip(gf.dispatch_indexes, types):
        _type.register_generic(gf, space.newint(index))


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


def extend(_type, mixins, methods):
    error.affirm_type(_type, space.isextendable)

    methods = _get_extension_methods(_type, mixins, methods)
    _type.add_methods(methods)
    return _type


############################################################
############################################################

def generic_with_hotpath(name, signature, hotpath):
    arity = api.length_i(signature)

    if arity == 0:
        error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR, space.newstring(u"Generic arity == 0"))
    if arity == 1:
        indexes = [0]
    else:
        indexes = []
        for i, sym in enumerate(signature):
            if api.to_s(sym).startswith("`"):
                indexes.append(i)

        if len(indexes) == 0:
            return error.throw_3(error.Errors.METHOD_SPECIALIZE_ERROR,
                                 space.newstring(u"Generic type variable not determined"), name, signature)

    h = HotPath(hotpath, arity) if hotpath is not None else None
    return W_Generic(name, arity, indexes, signature, h)


def generic(name, signature):
    return generic_with_hotpath(name, signature, None)


def get_method(process, gf, types):
    print "GET_METHOD", gf, types
    if space.istuple(types):
        types = tuples.to_list(types)

    if not space.islist(types):
        types = space.newlist([types])

    if api.length_i(types) != gf.dispatch_arity:
        return error.throw_3(error.Errors.KEY_ERROR,
                             space.newstring(u"Method not specified for signature"), gf, types)

    method = gf.dag.evaluate(process, types)
    if method is None:
        return error.throw_3(error.Errors.KEY_ERROR,
                             space.newstring(u"Method not specified for signature"), gf, types)
    return method
