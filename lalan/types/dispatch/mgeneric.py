from lalan.types.root import W_Hashable
from lalan.misc import platform
from lalan.builtins.hotpath import HotPath
from lalan.runtime import error
from lalan.types import api, space
from signature import newsignature
from dag import *

class SrategyType:
    ARITY_DISPATCH = 0
    SINGLE_DISPATCH = 1
    MULTIPLE_DISPATCH = 2


def _dict_key(obj1, obj2):
    assert space.isany(obj1)
    assert space.isany(obj2)
    v = obj1._equal_(obj2)
    return v


def _dict_hash(obj1):
    assert space.isany(obj1)
    return obj1._hash_()


def group_dict():
    from lalan.misc.platform import r_dict
    return r_dict(_dict_key, _dict_hash)

class W_MGeneric(W_Hashable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, arity, dispatch_indexes, args_signature, hotpath):
        W_Hashable.__init__(self)

        self.name = name
        self.arity = arity
        self.dispatch_indexes = dispatch_indexes

        self.arity = api.length_i(args_signature)
        self.dispatch_arity = len(dispatch_indexes)
        self.args_signature = args_signature
        self.signatures = []
        self.hot_path = hotpath
        self.count_call = 0
        self.dag = None

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
            return error.throw_2(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR, self, args)

        # print "METHOD CALL", method, args
        process.call_object(method, args)

    def _type_(self, process):
        return process.std.types.Generic

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)


def lookup_implementation(process, generic, args):
    dispatch_arg = api.at_index(args, generic.dispatch_arg_index)
    impl = api.dispatch(process, dispatch_arg, generic)
    return impl


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
    return W_MGeneric(name, arity, indexes, signature, h)


def generic(name, signature):
    return generic_with_hotpath(name, signature, None)

def specify(process, gf, types, method):
    if gf.dispatch_arity != api.length_i(types):
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Generic function arity inconsistant with specialisation arguments"))
    if gf.arity != method.arity:
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Bad method for specialisation, inconsistant arity"))

    gf.signatures.append(newsignature(process, types, method))
    gf.dag = _create_dag(gf, gf.signatures, gf.dispatch_arity)


def _create_dag(gf, signatures, arity):
    discriminators = []
    nodes = _make_nodes(gf, 0, arity, signatures, discriminators)
    dag = RootNode(nodes, discriminators)
    return dag


def _make_nodes(gf, index, arity, signatures, discriminators):
    if index == arity:
        leaf = _make_method_node(gf, signatures)
        # print "METHOD", index, leaf
        return leaf

    groups = group_dict()
    for signature in signatures:
        arg = signature.get_argument(index)
        if arg not in groups:
            groups[arg] = [signature]
        else:
            groups[arg].append(signature)

    nodes = []
    for arg, group in groups.iteritems():
        d = arg.discriminator(discriminators)
        children = _make_nodes(gf, index + 1, arity, group, discriminators)
        if len(children) == 1:
            nodes.append(SingleNode(d, children[0]))
        else:
            nodes.append(GroupNode(d, children))

    # print "NODES", index, nodes
    return nodes


def _make_method_node(gf, signatures):
    if len(signatures) != 1:
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Ambiguous method specialisation"))

    sig = signatures[0]
    return [LeafNode(sig.method)]


