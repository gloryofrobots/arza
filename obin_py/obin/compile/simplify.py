from obin.compile.parse.nodes import (node_type, node_arity,
                                      node_first, node_second, node_third, node_fourth, node_children, is_empty_node)
from obin.runtime import error
from obin.types import space, api, plist, environment, symbol as symbols, string as strings
from obin.builtins import lang_names

from obin.compile.parse import nodes


def simplify_error(compiler, code, node, message):
    from obin.compile.compiler import compile_error
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


def simplify_cons(compiler, code, node):
    left = node_first(node)
    right = node_second(node)
    return nodes.create_cons_node(node, left, right)


def simplify_delay(compiler, code, node):
    exp = node_first(node)
    fun_1_arg = nodes.create_fun_simple_node(node, nodes.empty_node(), nodes.list_node([exp]))
    return nodes.create_call_node_s(node, lang_names.DELAY, [fun_1_arg])


def simplify_union(compiler, code, node):
    name_node = node_first(node)
    types = node_second(node)
    name_1_arg = nodes.create_symbol_node(name_node, name_node)
    types_2_arg = nodes.create_list_node_from_list(node, types)

    call_node = nodes.create_call_node_s(node, lang_names.UNION, [name_1_arg, types_2_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_extend(compiler, code, node):
    typename_1_arg = node_first(node)
    mixins = node_second(node)
    methods = node_third(node)
    mixins_list = []
    methods_list = []
    for mixin_data in mixins:
        source = mixin_data[0]
        names = mixin_data[1]
        if is_empty_node(names):
            mixins_list.append(source)
        else:
            for name in names:
                methods_list.append(
                    nodes.create_tuple_node(name, [
                        name,
                        nodes.create_lookup_node(source, source, name)
                    ])
                )

    for method_data in methods:
        generic_name = method_data[0]
        impl = method_data[1]
        methods_list.append(
            nodes.create_tuple_node(generic_name, [
                generic_name,
                nodes.create_fun_node(generic_name, nodes.empty_node(), impl)
            ])
        )
    mixins_2_arg = nodes.create_list_node(node, mixins_list)
    methods_3_arg = nodes.create_list_node(node, methods_list)
    return nodes.create_call_node_s(node, lang_names.EXTEND, [typename_1_arg, mixins_2_arg, methods_3_arg])


def simplify_interface(compiler, code, node):
    name_node = node_first(node)
    name_1_arg = nodes.create_symbol_node(name_node, name_node)

    generics_node = node_second(node)
    generics_2_arg = nodes.create_list_node_from_list(node, generics_node)

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
    constraints_node = node_second(node)
    method_sources = node_third(node)

    trait_name_1_arg = nodes.create_symbol_node(trait_name_node, trait_name_node)
    constraints_2_arg = constraints_node

    methods = []
    for method_source in method_sources:
        generic_node = method_source[0]
        impl = method_source[1]

        methods.append(
            nodes.create_tuple_node(generic_node, [
                generic_node,
                nodes.create_fun_node(generic_node, nodes.empty_node(), impl)
            ])
        )
    methods_3_arg = nodes.create_list_node(node, methods)
    call_node = nodes.create_call_node_s(node, lang_names.TRAIT, [trait_name_1_arg, constraints_2_arg, methods_3_arg])
    trait_node = nodes.create_assign_node(node, trait_name_node, call_node)

    return trait_node

#
# First declare methods name. compiler second pass doesn`t walk through calls and assigns
# Possible fix -> separate ast for simple and complicated assigns NT_ASSIGN, NT_ASSIGN_MATCH
# methods = []
# # First declare methods name. compiler second pass doesn`t walk through calls and assigns
# # Possible fix -> separate ast for simple and complicated assigns NT_ASSIGN, NT_ASSIGN_MATCH
# for method_source in method_sources:
#     generic_node = method_source[0]
#     assign_void = nodes.create_assign_node(name_node, name_node, nodes.create_void_node(name_node))
#     methods.append(assign_void)
#
# for method_source in method_sources:
#     trait_1_arg = trait_name_node
#     name_node = method_source[0]
#     name_2_arg = nodes.create_symbol_node(name_node, name_node)
#
#     sig_3_arg = method_source[1]
#     default_impl = method_source[2]
#
#     if nodes.is_empty_node(default_impl):
#         impl_4_arg = nodes.create_void_node(name_2_arg)
#     else:
#         impl_4_arg = nodes.create_fun_node(name_2_arg, nodes.empty_node(), default_impl)
#
#     method_call_node = nodes.create_call_node_s(node,
#                                                 lang_names.GENERIC,
#                                                 [trait_1_arg, name_2_arg, sig_3_arg, impl_4_arg])
#     assign_node = nodes.create_assign_node(node, name_node, method_call_node)
#     methods.append(assign_node)
#
# call_node = nodes.create_call_node_s(node, lang_names.TRAIT, [trait_name_1_arg, constraints_2_arg, methods_3_arg])
# trait_node = nodes.create_assign_node(node, trait_name_node, call_node)
#
# return trait_node
