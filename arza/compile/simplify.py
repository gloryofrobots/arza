from arza.compile.parse.nodes import (node_type, node_arity, node_token, list_node,
                                      node_first, node_second, node_third, node_fourth, node_children, is_empty_node)
from arza.runtime import error
from arza.types import space, api, plist, environment, symbol as symbols, string as strings
from arza.builtins import lang_names
from arza.misc import platform

from arza.compile.parse import nodes, node_type as nt, basic


def simplify_error(compiler, code, node, message):
    from arza.compile.compiler import compile_error
    return compile_error(compiler, code, node, message)


def simplify_type(compiler, code, node):
    name_node = node_first(node)
    fields = node_second(node)
    mixins = node_third(node)

    name_1_arg = nodes.create_symbol_node(nodes.node_token(name_node), name_node)
    if is_empty_node(fields):
        fields_2_arg = nodes.create_empty_list_node(nodes.node_token(node))
    else:
        fields_2_arg = fields

    call_node = nodes.create_call_node_s(nodes.node_token(node), lang_names.TYPE,
                                         [name_1_arg, fields_2_arg])
    return nodes.create_assign_node(nodes.node_token(node), name_node, call_node)


def collapse_let(node):
    let_block = node_first(node)
    in_block = node_second(node)
    body = plist.concat(let_block, in_block)
    return body


def simplify_let(compiler, code, node):
    body = collapse_let(node)
    func = nodes.create_fun_0_node(nodes.node_token(node), nodes.empty_node(), body)
    return nodes.create_call_node_1(nodes.node_token(node),
                                    func,
                                    nodes.create_unit_node(nodes.node_token(node)))


def simplify_not(compiler, code, node):
    left = node_first(node)
    return nodes.create_not_call(nodes.node_token(node), left)


def simplify_cons(compiler, code, node):
    left = node_first(node)
    right = node_second(node)
    return nodes.create_cons_call(nodes.node_token(node), left, right)


def simplify_as(compiler, code, node):
    source = node_first(node)
    interfaces = node_second(node)
    return nodes.create_call_node_s(nodes.node_token(node), lang_names.CAST, [interfaces, source])


def simplify_describe(compiler, code, node):
    _type = node_first(node)
    interfaces = node_second(node)
    return nodes.create_call_node_s(nodes.node_token(node), lang_names.DESCRIBE, [_type, interfaces])


def _random_name(name):
    d = int((1 - platform.random()) * 10000000)
    name_s = api.to_s(name)
    name = space.newstring_s("%s_%d" % (name_s, d))
    return name


def _replace_name(node, level, names):
    ntype = node_type(node)

    if ntype == nt.NT_IMPORTED_NAME:
        name = nodes.imported_name_to_string(node)
        new_node = nodes.create_name_node(nodes.node_token(node), name)
        return _replace_name(new_node, level, names)

    if ntype != nt.NT_NAME:
        return None
    for old_name, new_name in names:
        if api.equal_b(old_name, nodes.node_value(node)):
            return nodes.create_name_node(nodes.node_token(node), new_name)

    return node


def simplify_def_plus(compiler, code, node):
    super_name = nodes.node_first(node)
    def_method = nodes.node_second(node)
    func, signature, method, ast, outers_list = _simplify_def(compiler, code, def_method)

    token = nodes.node_token(node)
    # f1 = nodes.create_fun_node(token, nodes.empty_node(), method)
    f1 = method
    wrapper = nodes.create_fun_1_node(
        token, nodes.empty_node(),
        super_name,
        f1
    )
    call_override = nodes.create_call_node_s(token, lang_names.OVERRIDE_HELPER, [func, signature, wrapper])
    return nodes.create_call_node_s(token, lang_names.OVERRIDE,
                                    [func, signature, call_override, ast, outers_list])


def simplify_def(compiler, code, node):
    func, signature, method, ast, outers_list = _simplify_def(compiler, code, node)
    return nodes.create_call_node_s(nodes.node_token(node), lang_names.SPECIFY,
                                    [func, signature, method, ast, outers_list])


def _simplify_def(compiler, code, node):
    func = node_first(node)
    signature = node_second(node)
    method = node_third(node)
    pattern = node_fourth(node)

    if node_type(pattern) == nt.NT_WHEN:
        args = node_first(pattern)
        guard = node_second(pattern)

        # names occurred in guard must be renamed (real name + random suffix)
        # and saved in generic function

        arg_names = nodes.find_names(args)
        guard_names = nodes.find_names(guard)
        outer_names = plist.diff(guard_names, arg_names)
        randomized_outer_names = plist.fmap(_random_name, outer_names)
        pairs = zip(outer_names, randomized_outer_names)
        new_guard = basic.transform(guard, _replace_name, pairs)

        pattern = nodes.create_when_node(nodes.node_token(pattern), args, new_guard)
        outers = []
        for old_name, new_name in pairs:
            outers.append(nodes.create_tuple_node(
                nodes.node_token(pattern),
                [
                    nodes.create_symbol_node_string(nodes.node_token(pattern), new_name),
                    nodes.create_name_node(nodes.node_token(pattern), old_name)
                ]
            ))
        outers_list = nodes.create_list_node(nodes.node_token(pattern), outers)
        #
        # print "NAMES", arg_names, guard_names, outer_names, randomized_outer_names
        # print "NEW_GUARD", new_guard
    else:
        outers_list = nodes.create_empty_list_node(nodes.node_token(pattern))

    ast = nodes.create_literal_node(nodes.node_token(pattern), pattern)
    return func, signature, method, ast, outers_list


def simplify_interface(compiler, code, node):
    name_node = node_first(node)
    name_1_arg = nodes.create_symbol_node(nodes.node_token(name_node), name_node)

    generics_2_arg = node_second(node)
    subs_3_arg = node_third(node)

    call_node = nodes.create_call_node_s(nodes.node_token(node), lang_names.INTERFACE,
                                         [name_1_arg, generics_2_arg, subs_3_arg])
    return nodes.create_assign_node(nodes.node_token(node), name_node, call_node)


def simplify_receive(compiler, code, node):
    branches = node_first(node)
    fun_node = nodes.create_nameless_fun(node_token(node), branches)

    return nodes.create_call_node_s(nodes.node_token(node), lang_names.RECEIVE_HELPER, [fun_node])


def simplify_generic(compiler, code, node):
    name_node = node_first(node)
    name_1_arg = nodes.create_symbol_node(nodes.node_token(name_node), name_node)

    symbols_2_arg = node_second(node)

    call_node = nodes.create_call_node_s(nodes.node_token(node), lang_names.GENERIC, [name_1_arg, symbols_2_arg])
    return nodes.create_assign_node(nodes.node_token(node), name_node, call_node)


########################3

def create_infix_lookup(path):
    result, tail = plist.split(path)
    if plist.is_empty(tail):
        return result

    return nodes.create_lookup_node(nodes.node_token(result), create_infix_lookup(tail), result)


def simplify_lense(compiler, code, node):
    """
    transforms
    $(d.s1.s2)
    into
    arza:lang:lense(d, (source) -> source.s1.s2, (value, source) -> source.{s1.s2 = value})
    """

    source = node_first(node)
    setter_path = node_second(node)
    token = node_token(source)
    source_name = nodes.create_name_node_s(token, "source")
    value_name = nodes.create_name_node_s(token, "value")

    ## GETTER
    getter_path = nodes.create_lookup_node(token, source_name, setter_path)
    getter_path_list = basic.flatten_infix(getter_path, nt.NT_LOOKUP)
    getter_path_list = plist.reverse(getter_path_list)
    getter_body = create_infix_lookup(getter_path_list)

    getter = nodes.create_lambda_node(token, nodes.create_tuple_node(token, [source_name]),
                                      getter_body)

    ## SETTER
    # pair = list_node([setter_path, value_name])
    pair = _create_modify_item(nt.NT_ASSIGN, node_token(setter_path), setter_path, value_name)
    setter_body = nodes.create_modify_node(token, source_name, list_node([pair]))
    setter = nodes.create_lambda_node(token, nodes.create_tuple_node(token, [value_name, source_name]),
                                      setter_body)

    call_node = nodes.create_call_node_s(nodes.node_token(node), lang_names.LENSE,
                                         [source, getter, setter])
    return call_node


###############################


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

    funcs = (nodes.create_name_node_s(nodes.node_token(node), lang_names.PUT),
             nodes.create_name_node_s(nodes.node_token(node), lang_names.PUT_DEFAULT),
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
        return _transform_modify(compiler, node,
                                 funcs,
                                 nodes.create_call_node_3(nodes.node_token(node), func, new_key, new_value, source),
                                 tail)
    # else:
    #     # ensure symbol
    #     key = nodes.ensure_symbol_node_from_name(node_token(key), key)

    # transform all @ nodes to proper paths
    transformed_bind = nodes.create_lookup_node(node_token(key), source, key)
    value = basic.transform(value, _transfom_binds_callback, dict(path=transformed_bind, stop_level=-1))
    func = _choose_modify_func(ntype, funcs)
    return _transform_modify(compiler, node,
                             funcs,
                             nodes.create_call_node_3(nodes.node_token(node), func, key, value, source),
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
    if node_type(decorated) == nt.NT_FUN:
        return _decorate_fun(decorated, decorators)
    elif node_type(decorated) == nt.NT_DEF:
        return _decorate_def(decorated, decorators)
    elif node_type(decorated) == nt.NT_DEF_PLUS:
        return _decorate_def_plus(decorated, decorators)
    else:
        assert False


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
