from arza.compile.parse.nodes import (node_type, node_arity,
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

    name_1_arg = nodes.create_symbol_node(name_node, name_node)
    if is_empty_node(fields):
        fields_2_arg = nodes.create_empty_list_node(node)
    else:
        fields_2_arg = fields

    call_node = nodes.create_call_node_s(node, lang_names.TYPE, [name_1_arg, fields_2_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_let(compiler, code, node):
    let_block = node_first(node)
    in_block = node_second(node)
    body = plist.concat(let_block, in_block)
    func = nodes.create_fun_simple_node(node, nodes.empty_node(), body)
    return nodes.create_call_node_1(node, func, nodes.create_unit_node(node))


def simplify_not(compiler, code, node):
    left = node_first(node)
    return nodes.create_not_call(node, left)


def simplify_cons(compiler, code, node):
    left = node_first(node)
    right = node_second(node)
    return nodes.create_cons_call(node, left, right)


def simplify_use(compiler, code, node):
    trait_name = node_first(node)
    exported = node_second(node)
    types = node_third(node)
    return nodes.create_call_node_s(node, lang_names.USE_TRAIT, [trait_name, exported, types])


def _random_name(name):
    d = int((1 - platform.random()) * 10000000)
    name_s = api.to_s(name)
    name = space.newstring_s("%s_%d" % (name_s, d))
    return name


def _replace_name(node, names):
    ntype = node_type(node)

    if ntype == nt.NT_IMPORTED_NAME:
        name = nodes.imported_name_to_string(node)
        new_node = nodes.create_name_node(node, name)
        return _replace_name(new_node, names)

    if ntype != nt.NT_NAME:
        return None
    for old_name, new_name in names:
        if api.equal_b(old_name, nodes.node_value(node)):
            return nodes.create_name_node(node, new_name)

    return node


def simplify_def(compiler, code, node):
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

        pattern = nodes.create_when_node(pattern, args, new_guard)
        outers = []
        for old_name, new_name in pairs:
            outers.append(nodes.create_tuple_node(
                pattern,
                [
                    nodes.create_symbol_node_string(pattern, new_name),
                    nodes.create_name_node(pattern, old_name)
                ]
            ))
        outers_list = nodes.create_list_node(pattern, outers)
        #
        # print "NAMES", arg_names, guard_names, outer_names, randomized_outer_names
        # print "NEW_GUARD", new_guard
    else:
        outers_list = nodes.create_empty_list_node(pattern)

    ast = nodes.create_literal_node(pattern, pattern)
    return nodes.create_call_node_s(node, lang_names.SPECIFY, [func, signature, method, ast, outers_list])


def simplify_interface(compiler, code, node):
    name_node = node_first(node)
    name_1_arg = nodes.create_symbol_node(name_node, name_node)

    generics_2_arg = node_second(node)

    call_node = nodes.create_call_node_s(node, lang_names.INTERFACE, [name_1_arg, generics_2_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_generic(compiler, code, node):
    name_node = node_first(node)
    name_1_arg = nodes.create_symbol_node(name_node, name_node)

    symbols_2_arg = node_second(node)

    call_node = nodes.create_call_node_s(node, lang_names.GENERIC, [name_1_arg, symbols_2_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_trait(compiler, code, node):
    trait_name_node = node_first(node)
    trait_name_1_arg = nodes.create_symbol_node(trait_name_node, trait_name_node)
    signature_2_arg = node_second(node)
    constraints_3_arg = node_third(node)
    methods_4_arg = node_fourth(node)

    call_node = nodes.create_call_node_s(node, lang_names.TRAIT,
                                         [trait_name_1_arg,
                                          signature_2_arg,
                                          constraints_3_arg,
                                          methods_4_arg])

    trait_node = nodes.create_assign_node(node, trait_name_node, call_node)
    return trait_node
