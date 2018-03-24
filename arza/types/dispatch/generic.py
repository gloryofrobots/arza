from arza.types.root import W_Hashable, W_Root
from arza.misc import platform
from arza.runtime import error
from arza.builtins import lang_names
from arza.types import api, space, plist, tuples
from arza.compile.parse import nodes
from arza.compile import compiler
from signature import newsignature, newuniquesignature
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
    from arza.misc.platform import r_dict
    return r_dict(_dict_key, _dict_hash)


class W_Generic(W_Hashable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, arity, args_signature, cache_mask):
        W_Hashable.__init__(self)
        self.name = name
        self.arity = arity
        self.dispatch_indexes = [i for i in range(len(args_signature))]
        self.dispatch_arity = len(self.dispatch_indexes)
        # self.interfaces = plist.empty()
        self.arity = api.length_i(args_signature)
        self.args_signature = args_signature
        self.signatures = []
        self.unique_signatures = []
        self.count_call = 0
        self.env = space.newemptyenv(self.name)
        self.cache_mask = cache_mask
        self.dag = None
        self.cache = space.newassocarray()

    def get_types(self):
        types = plist.empty()
        for sig in self.signatures:
            if not api.contains_b(types, sig.types):
                types = plist.cons(sig.types, types)

        return plist.reverse(types)

    def is_implemented_for_type(self, _type, interfaces, position, strictmode=False):
        error.affirm_type(_type, space.isdatatype)
        for sig in self.signatures:
            if sig.can_dispatch_on_type(_type, interfaces, position, strictmode):
                return True

        return False

    # def register_interface(self, interface, position):
    #     self.interfaces = plist.cons(space.newtuple([interface, position]), self.interfaces)

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
        # if self.hot_path is not None:
        #     res = self.hot_path.apply(process, args)
        #     if res is not None:
        #         return res
        _types = []
        for i in range(len(args)):
            arg = args[i]
            cache_mask = self.cache_mask[i]
            if cache_mask == 0:
                _type = api.get_type(process, arg)
            else:
                _type = arg
            _types.append(_type)
        cache_req = space.newtuple(_types)
        cache_method = api.lookup(self.cache, cache_req, space.newvoid())

        if space.isvoid(cache_method):
            method = self.dag.evaluate(process, args)
            if not method:
                return error.throw_4(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR,
                                     self,
                                     tuples.types_tuple(process, args),
                                     args,
                                     space.newlist(self.signatures))
            api.put(self.cache, cache_req, method)
        else:
            method = cache_method

        assert method is not self
        api.call(process, method, args)

    def _type_(self, process):
        return process.std.types.Generic

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def override_signature(self, process, signature):
        new_signatures = []
        for sig in self.signatures:
            if not signature.equal(sig):
                new_signatures.append(sig)

        self.signatures = new_signatures
        self.add_signature(process, signature)

    def add_signature(self, process, signature):
        self.cache = space.newassocarray()
        self.unique_signatures = []
        self.signatures.append(signature)
        discriminators = []
        nodes = self._make_nodes(process, 0, self.dispatch_arity, self.signatures, discriminators)
        self.dag = RootNode(nodes, discriminators)

    def get_method_types(self):
        types = []
        for sig in self.unique_signatures:
            types.append(sig.types)
        return types

    def get_method(self, types):
        for sig in self.unique_signatures:
            if sig.consists_of(types):
                return sig.method
        return space.newvoid()

    def _make_nodes(self, process, index, arity, signatures, discriminators):
        if index == arity:
            leaf = self._make_method_node(process, signatures)
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
            children = self._make_nodes(process, index + 1, arity, group, discriminators)
            if len(children) == 1:
                nodes.append(SingleNode(d, children[0]))
            else:
                nodes.append(GroupNode(d, children))

        # print "NODES", index, nodes
        return nodes

    def _sort_signatures(self, sig1, sig2):
        w1 = sig1.get_weight()
        w2 = sig2.get_weight()
        if w1 > w2:
            return -1
        elif w2 > w1:
            return 1
        else:
            return 0

    def _make_method_node(self, process, sigs):
        signatures = sorted(sigs, self._sort_signatures)
        sig = signatures[0]
        if len(signatures) != 1 or nodes.is_guarded_pattern(sig.pattern):
            method = conflict_resolver(process, self, signatures)
        else:
            method = sig.method

        # return error.throw_3(error.Errors.METHOD_SPECIALIZE_ERROR,
        #                      self,
        #                      space.newlist(signatures),
        #                      space.newstring(u"Ambiguous generic specialisation"))
        unique = newuniquesignature(process, sig, method)
        self.unique_signatures.append(unique)
        return [LeafNode(sig, method)]


class ConflictResolverCallback(W_Root):
    def __init__(self, signatures, fn, args):
        self.fn = fn
        self.args = args
        self.signatures = signatures
        self.waiting = False

    def on_complete(self, process, result):
        if self.waiting:
            return result
        # print "ON COMPL", result
        idx = api.to_i(result)
        method = self.signatures[idx].method
        # print "COMPL", idx, method
        self.waiting = True
        return process.call_object(method, self.args)

    def _to_routine_(self, stack, args):
        from arza.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_complete, None, self.fn, args)
        return routine


class ConflictResolver(W_Root):
    def __init__(self, signatures, fn):
        self.fn = fn
        self.signatures = signatures

    def _call_(self, process, args):
        fn = space.newfunc_from_source(self.fn, process.modules.prelude)
        process.call_object(ConflictResolverCallback(self.signatures, fn, args), args)

    def _to_string_(self):
        return api.to_s(self.fn)


def conflict_resolver(process, gf, signatures):
    funcs = []
    for i, sig in enumerate(signatures):
        # put outers in generics compile environment
        for t in sig.outers:
            name = api.first(t)
            obj = api.second(t)
            api.put(gf.env, name, obj)

        body = nodes.create_int_node(nodes.node_token(sig.pattern), i)
        # body = nodes.create_literal_node(sig.pattern, sig.method)

        funcs.append(nodes.list_node([
            sig.pattern, nodes.list_node([body])
        ]))
    fn_node = nodes.create_fun_node(nodes.node_token(signatures[0].pattern),
                                    nodes.empty_node(),
                                    nodes.list_node(funcs))
    fn = compiler.compile_function_ast(process, gf.env, fn_node)
    return ConflictResolver(signatures, fn)


def _make_signature(process, gf, types, method, pattern, outers):
    any = process.std.interfaces.Any

    _types = space.newlist([
                               any if space.isvoid(_type) else _type for _type in types
                               ])

    if gf.dispatch_arity != api.length_i(types):
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Generic function arity inconsistent with specialisation arguments"))

    if gf.arity != method.arity:
        # print gf, method, gf.arity, method.arity
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Bad method for specialisation, inconsistent arity"))
    return newsignature(process, _types, method, pattern, outers)


def specify(process, gf, types, method, pattern, outers):
    sig = _make_signature(process, gf, types, method, pattern, outers)
    gf.add_signature(process, sig)
    # for index, _type in zip(gf.dispatch_indexes, _types):
    #     _type.register_generic(gf, space.newint(index))


def override(process, gf, types, method, pattern, outers):
    sig = _make_signature(process, gf, types, method, pattern, outers)
    gf.override_signature(process, sig)


def get_method(process, gf, types):
    method = gf.get_method(types)
    if space.isvoid(method):
        return error.throw_3(error.Errors.KEY_ERROR,
                             space.newstring(u"Method not specified for signature"), gf, types)

    return method
    # if space.istuple(types):
    #     types = tuples.to_list(types)
    #
    # if not space.islist(types):
    #     types = space.newlist([types])
    #
    # if api.length_i(types) != gf.dispatch_arity:
    #     return error.throw_3(error.Errors.KEY_ERROR,
    #                          space.newstring(u"Method not specified for signature"), gf, types)
    #
    # method = gf.dag.evaluate(process, types)
    # if method is None:
    #     return error.throw_3(error.Errors.KEY_ERROR,
    #                          space.newstring(u"Method not specified for signature"), gf, types)
    # return method


def signatures(process, gf):
    return space.newlist(gf.get_method_types())


############################################################
############################################################


def generic(process, name, signature):
    arity = api.length_i(signature)

    if arity == 0:
        error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR, space.newstring(u"Generic arity == 0"))

    cache_mask = []
    args = []
    for arg in signature:
        if space.istuple(arg):
            argtype = api.at_index(arg, 0)
            real_arg = api.at_index(arg, 1)
            if api.equal_b(argtype, space.newsymbol_s(process, lang_names.SVALUEOF)):
                argcache = 1
            else:
                return error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR,
                                     space.newstring(u"Invalid generic signature param"))
        else:
            argcache = 0
            real_arg = arg

        args.append(real_arg)
        cache_mask.append(argcache)

    return W_Generic(name, arity, space.newlist(args), cache_mask)
