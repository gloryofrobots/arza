from capy.compile.parse.nodes import (node_type, node_arity, node_token, list_node,
                                      node_first, node_second, node_third, node_fourth, node_children, is_empty_node)
from capy.runtime import error
from capy.types import space, api, plist, environment, symbol as symbols, string as strings
from capy.builtins import lang_names
from capy.misc import platform

from capy.compile.parse import nodes, node_type as nt, basic


def simplify_not(compiler, code, node):
    left = node_first(node)
    return nodes.create_not_call(nodes.node_token(node), left)


def _random_name(name):
    d = int((1 - platform.random()) * 10000000)
    name_s = api.to_s(name)
    name = space.newstring_s("%s_%d" % (name_s, d))
    return name


def _replace_name(node, level, names):
    ntype = node_type(node)

    if ntype != nt.NT_NAME:
        return None
    for old_name, new_name in names:
        if api.equal_b(old_name, nodes.node_value(node)):
            return nodes.create_name_node(nodes.node_token(node), new_name)

    return node


def simplify_class(compiler, code, node):
    token = nodes.node_token(node)
    name_node = node_first(node)
    parent_node = node_second(node)
    code = node_third(node)
    name_1_arg = nodes.create_symbol_node(nodes.node_token(name_node), name_node)
    if nodes.is_empty_node(parent_node):
        parent_1_arg = nodes.create_nil_node(token)
    else:
        parent_1_arg = parent_node

    body = plist.append(code, nodes.create_call_node_s(token, lang_names.ENV, []))
    func = nodes.create_fun_0_node(token, nodes.empty_node(), body)
    env_call_3_arg = nodes.create_call_node_0(token, func)

    call_node = nodes.create_call_node_s(nodes.node_token(node), lang_names.DEFCLASS,
                                         [name_1_arg, parent_1_arg, env_call_3_arg])
    return nodes.create_assign_node(nodes.node_token(node), name_node, call_node)


########################3


def simplify_modify(compiler, code, node):
    """
    Complicated transformation

    this expression :
    let d1 = d.{
        s1.s2.x = 1,
        s1.s2 = @,
        y = @ + f(@)
    }

    will be transformed into

    let d1 = d.{
        s1 = d.s1.{
            s2 = d.s1.s2.{
                x = 1
            }
        },
        s1 = d.s1.{
            s2 = d.s1.s2
        },
        y = d.y + f(d.y)
    }
    """
    # print "------------SIMPLIFY"
    source = nodes.node_first(node)
    modifications = nodes.node_second(node)

    funcs = (nodes.create_symbol_node_s(nodes.node_token(node), lang_names.PUT),
             nodes.create_symbol_node_s(nodes.node_token(node), lang_names.PUT_DEFAULT),
             )
    return _transform_modify(compiler, node,
                             funcs,
                             source,
                             modifications
                             )


def _transfom_binds_callback(node, level, state):
    """
    callback used for transforming @ nodes into lookup chains (state["path"])
    state[stop_level] will store level after which @ nodes will not be processed
    this is necessarry because lookup information for deep nested @ nodes have not been calculated yet
    """
    stop_level = state["stop_level"]
    # print "0: ", level, stop_level, node_type(node)
    if stop_level > 0 and stop_level < level:
        # print "1: ", level, stop_level
        return None

    t = node_type(node)
    if t == nt.NT_MODIFY and stop_level < 0:
        state["stop_level"] = level + 1
        # print "2: ", level, data["stop_level"]

    if t != nt.NT_BIND:
        return None

    return state["path"]


def _choose_modify_func(ntype, funcs):
    if ntype == nt.NT_ASSIGN:
        return funcs[0]
    else:
        return funcs[1]


def _create_modify_item(ntype, token, key, value):
    return nodes.node_2(ntype, token, key, value)


def _transform_modify(compiler, node, funcs, source, modifications):
    """
    transforms modify x.{a=1, b=2, 0=4} into series of puts
    put 0 4 (put b 2 (put a 1 x))

    and
    let d1 = d.{
        s1.s2.x = 1,
    }
    transforms into
    let d1 = d.{
        s1 = d.s1.{
            s2 = d.s1.s2.{
                x = 1
            }
        },
    }
    Algo is somewhat convoluted
    This is recursive function. Instead of transforming all expression at once it transforms
    only its first level and stores information for next level in generated nodes
    then it returns generated nodes to the compiler that will call this transfromation again for the next level after
    it compiles simplified first
    Also all @ tokens will be replaced by appropriate lookup chains
    """
    if plist.is_empty(modifications):
        # end of recursion. processed all nodes from this levels into call chain
        return source
    # for m in modifications:
    #     assert not space.islist(m)
    m, tail = plist.split(modifications)
    key = node_first(m)
    value = node_second(m)
    ntype = node_type(m)

    k_type = node_type(key)
    if k_type == nt.NT_LOOKUP:
        # This means we need to create modify node and store path to this node in its first child (source)
        first = node_first(key)
        other_keys = node_second(key)

        # creating path
        # new_key = nodes.ensure_symbol_node_from_name(node_token(key), first)
        new_key = first
        new_source = nodes.create_lookup_node(node_token(new_key), source, new_key)

        # creating modify node
        # new_pair = list_node([other_keys, value])
        new_pair = _create_modify_item(ntype, node_token(new_key), other_keys, value)
        new_value = nodes.create_modify_node(node_token(new_key), new_source, list_node([new_pair]))

        func = _choose_modify_func(ntype, funcs)
        # put = nodes.create_call_node_3(nodes.node_token(node), func, new_key, new_value, source),
        put = nodes.create_lookup_call(nodes.node_token(node), source, func, [new_key, new_value])
        return _transform_modify(compiler, node,
                                 funcs,
                                 put,
                                 tail)

    # transform all @ nodes to proper paths
    transformed_bind = nodes.create_lookup_node(node_token(key), source, key)
    value = basic.transform(value, _transfom_binds_callback, dict(path=transformed_bind, stop_level=-1))
    func = _choose_modify_func(ntype, funcs)
    # put = nodes.create_call_node_3(nodes.node_token(node), func, key, value, source),
    put = nodes.create_lookup_call(nodes.node_token(node), source, func, [key, value])
    return _transform_modify(compiler, node,
                             funcs,
                             put,
                             tail)


###################################################
## DECORATOR
###################################################

def _flatten_decorators(node, result):
    decorated = node_third(node)
    if node_type(decorated) == nt.NT_DECORATOR:
        return _flatten_decorators(decorated, plist.cons(node, result))
    else:
        return decorated, plist.reverse(plist.cons(node, result))


def _make_decorator_call_chain(subj, decorators):
    dec, tl = plist.split(decorators)
    name = node_first(dec)
    args = node_second(dec)

    if plist.is_empty(tl):
        args = plist.cons(subj, args)
    else:
        args = plist.cons(_make_decorator_call_chain(subj, tl), args)

    return nodes.create_call_node(node_token(name), name, args)


def simplify_decorator(compiler, code, node):
    """
    @f1(1, 2)
    @f2(3)
    fun f() =1

    f = f1(f2(f, 3), 1, 2)
    """

    decorated, decorators = _flatten_decorators(node, plist.empty())
    ntype = node_type(decorated)
    if ntype == nt.NT_FUN:
        return _decorate_fun(decorated, decorators)
    elif ntype == nt.NT_DEF:
        return _decorate_def(decorated, decorators)
    elif ntype == nt.NT_DEF_PLUS:
        return _decorate_def_plus(decorated, decorators)
    elif ntype == nt.NT_TYPE:
        return _decorate_type(decorated, decorators)
    else:
        assert False


def _decorate_type(subj, decorators):
    name_node = nodes.node_first(subj)
    fields = nodes.node_second(subj)
    init = nodes.node_third(subj)

    if is_empty_node(fields):
        fields = nodes.create_empty_list_node(nodes.node_token(subj))

    if is_empty_node(init):
        init = nodes.create_unit_node(nodes.node_token(subj))

    token = node_token(subj)
    dec_arg = nodes.create_array_node(token, [fields, init])

    decorator_call = _make_decorator_call_chain(dec_arg, decorators)
    temp_name = nodes.create_random_type_decorator_name(token)
    checked_call = nodes.create_call_node_s(token, lang_names.AFFIRM_TYPE_DECORATOR,
                                            [decorator_call])
    assign = nodes.create_assign_node(token, temp_name, checked_call)

    name_1_arg = nodes.create_symbol_node(nodes.node_token(name_node), name_node)
    fields_2_arg = nodes.create_lookup_index_node(token, temp_name, 0)
    construct_3_arg = nodes.create_lookup_index_node(token, temp_name, 1)
    type_call = _generate_type_call(token, name_node, name_1_arg, fields_2_arg, construct_3_arg)
    return list_node([assign, type_call])


def _decorate_def(subj, decorators):
    func = node_first(subj)
    signature = node_second(subj)
    method = node_third(subj)
    pattern = node_fourth(subj)
    decorator_call = _make_decorator_call_chain(method, decorators)
    return nodes.node_4(nt.NT_DEF, node_token(subj), func, signature, decorator_call, pattern)


def _decorate_def_plus(decorated, decorators):
    super_name = node_first(decorated)
    subj = node_second(decorated)

    method = _decorate_def(subj, decorators)
    return nodes.node_2(nt.NT_DEF_PLUS, node_token(decorated), super_name, method)


def _decorate_fun(subj, decorators):
    subj_name = nodes.node_first(subj)
    decorator_call = _make_decorator_call_chain(subj_name, decorators)
    # overwrite decorated function here
    assign = nodes.node_2(nt.NT_ASSIGN_FORCE, node_token(subj), subj_name, decorator_call)
    return list_node([subj, assign])
