from lalan.types.root import W_Hashable, W_Root
from lalan.misc import platform
from lalan.runtime import error
from lalan.types import api, space, plist, tuples
from lalan.compile.parse import nodes
from lalan.compile import compiler
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

    def __init__(self, name, arity, args_signature):
        W_Hashable.__init__(self)

        self.name = name
        self.arity = arity
        self.dispatch_indexes = [i for i in range(len(args_signature))]
        self.dispatch_arity = len(self.dispatch_indexes)
        self.interfaces = plist.empty()
        self.arity = api.length_i(args_signature)
        self.args_signature = args_signature
        self.signatures = []
        self.count_call = 0
        self.env = space.newemptyenv(self.name)
        self.dag = None

    def get_types(self):
        types = plist.empty()
        for sig in self.signatures:
            if not api.contains_b(types, sig.types):
                types = plist.cons(sig.types, types)

        return plist.reverse(types)

    def register_interface(self, interface, position):
        self.interfaces = plist.cons(space.newtuple([interface, position]), self.interfaces)

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

        dispatch_args = space.newtuple([args[i] for i in self.dispatch_indexes])
        method = self.dag.evaluate(process, dispatch_args)
        # print "GEN CALL", str(method)
        # method = lookup_implementation(process, self, args)
        assert method is not self

        if not method:
            return error.throw_3(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR,
                                 self,
                                 args,
                                 space.newlist(self.signatures))

        api.call(process, method, args)
        # print "METHOD CALL", method, args
        # process.call_object(method, args)

    def _type_(self, process):
        return process.std.types.Generic

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def add_signature(self, process, signature):
        self.signatures.append(signature)
        discriminators = []
        nodes = self._make_nodes(process, 0, self.dispatch_arity, self.signatures, discriminators)
        self.dag = RootNode(nodes, discriminators)

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

    def _make_method_node(self, process, signatures):
        sig = signatures[0]
        if len(signatures) != 1 or nodes.is_guarded_pattern(sig.pattern):
            return [LeafNode(conflict_resolver(process, self, signatures))]
            # return error.throw_3(error.Errors.METHOD_SPECIALIZE_ERROR,
            #                      self,
            #                      space.newlist(signatures),
            #                      space.newstring(u"Ambiguous generic specialisation"))


        return [LeafNode(sig.method)]


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
        from lalan.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_complete, None, self.fn, args)
        return routine


class ConflictResolver(W_Root):
    def __init__(self, signatures, fn):
        self.fn = fn
        self.signatures = signatures

    def _call_(self, process, args):
        fn = space.newfunc_from_source(self.fn, process.modules.prelude)
        process.call_object(ConflictResolverCallback(self.signatures, fn, args), args)


def conflict_resolver(process, gf, signatures):
    funcs = []
    for i, sig in enumerate(signatures):
        # put outers in generics compile environment
        for t in sig.outers:
            name = api.first(t)
            obj = api.second(t)
            api.put(gf.env, name, obj)

        body = nodes.create_int_node(sig.pattern, i)
        # body = nodes.create_literal_node(sig.pattern, sig.method)

        funcs.append(nodes.list_node([
            sig.pattern, nodes.list_node([body])
        ]))
    fn_node = nodes.create_fun_node(signatures[0].pattern, nodes.empty_node(), nodes.list_node(funcs))
    fn = compiler.compile_function_ast(process, gf.env, fn_node)
    return ConflictResolver(signatures, fn)


def specify(process, gf, types, method, pattern, outers):
    any = process.std.interfaces.Any
    _types = space.newlist([
                               any if space.isvoid(_type) else _type for _type in types
                               ])

    if gf.dispatch_arity != api.length_i(types):
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Generic function arity inconsistent with specialisation arguments"))
    if gf.arity != method.arity:
        return error.throw_2(error.Errors.METHOD_SPECIALIZE_ERROR,
                             gf,
                             space.newstring(u"Bad method for specialisation, inconsistent arity"))

    gf.add_signature(process, newsignature(process, _types, method, pattern, outers))
    for index, _type in zip(gf.dispatch_indexes, _types):
        _type.register_generic(gf, space.newint(index))


def get_method(process, gf, types):
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



############################################################
############################################################

def generic_with_hotpath(name, signature):
    arity = api.length_i(signature)

    if arity == 0:
        error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR, space.newstring(u"Generic arity == 0"))

    return W_Generic(name, arity, signature)


def generic(name, signature):
    return generic_with_hotpath(name, signature)






# def _find_constraint_generic(generic, pair):
#     return api.equal_b(pair[0], generic)
#
#
# def _get_extension_methods(_type, _mixins, _methods):
#     # BETTER WAY IS TO MAKE DATATYPE IMMUTABLE
#     # AND CHECK CONSTRAINTS AFTER SETTING ALL METHO
#     total = plist.empty()
#     constraints = plist.empty()
#     error.affirm_type(_methods, space.islist)
#     for trait in _mixins:
#         error.affirm_type(trait, space.istrait)
#         constraints = plist.concat(constraints, trait.constraints)
#         trait_methods = trait.to_list()
#         total = plist.concat(trait_methods, total)
#
#     total = plist.concat(_methods, total)
#
#     for iface in constraints:
#         for generic in iface.generics:
#
#             if not plist.contains_with(total, generic,
#                                        _find_constraint_generic):
#                 return error.throw_4(error.Errors.CONSTRAINT_ERROR,
#                                      _type, iface, generic,
#                                      space.newstring(
#                                          u"Dissatisfied trait constraint"))
#
#     result = plist.empty()
#     for pair in total:
#         generic = pair[0]
#         if plist.contains_with(result, generic, _find_constraint_generic):
#             continue
#
#         result = plist.cons(pair, result)
#
#     return plist.reverse(result)
#
#
# def extend(_type, mixins, methods):
#     error.affirm_type(_type, space.isextendable)
#
#     methods = _get_extension_methods(_type, mixins, methods)
#     _type.add_methods(methods)
#     return _type
#

