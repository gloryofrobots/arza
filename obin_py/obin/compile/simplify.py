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
    constructor = node_third(node)

    name_1_arg = nodes.create_symbol_node(name_node, name_node)
    if is_empty_node(fields):
        fields_2_arg = nodes.create_empty_list_node(node)
        constructor_3_arg = nodes.create_void_node(node)
    else:
        fields_2_arg = fields
        constructor_3_arg = nodes.create_fun_node(node, nodes.empty_node(), constructor)

    call_node = nodes.create_call_node_s(node, lang_names.TYPE, [name_1_arg, fields_2_arg, constructor_3_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_let(compiler, code, node):
    let_block = node_first(node)
    in_block = node_second(node)
    body = plist.concat(let_block, in_block)
    func = nodes.create_fun_simple_node(node, nodes.empty_node(), body)
    return nodes.create_call_node_1(node, func, nodes.create_unit_node(node))


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


def simplify_implement(compiler, code, node):
    traitname_1_arg = node_first(node)
    typename_2_arg = node_second(node)
    methods = node_third(node)

    methods_list = []
    for method in methods:
        method_name = method[0]
        method_impl = method[1]
        method_arg = nodes.create_tuple_node(method_name, [
            method_name,
            nodes.create_fun_node(method_name, nodes.empty_node(), method_impl)
        ])

        methods_list.append(method_arg)

    methods_3_arg = nodes.create_list_node(node, methods_list)

    return nodes.create_call_node_s(node, lang_names.IMPLEMENT, [traitname_1_arg, typename_2_arg, methods_3_arg])


def simplify_extend(compiler, code, node):
    typename_1_arg = node_first(node)
    traits = node_second(node)
    traits_list = []
    for trait_data in traits:
        trait_name = trait_data[0]
        impls = trait_data[1]
        # MIXINS suuport
        if nodes.is_list_node(impls):
            methods_list = []
            for method in impls:
                method_name = method[0]
                method_impl = method[1]
                method_arg = nodes.create_tuple_node(method_name, [
                    method_name,
                    nodes.create_fun_node(method_name, nodes.empty_node(), method_impl)
                ])

                methods_list.append(method_arg)

            implementation = nodes.create_list_node(trait_name, methods_list)
        else:
            implementation = impls

        traits_list.append(nodes.create_list_node(trait_name, [trait_name, implementation]))

    traits_2_arg = nodes.create_list_node(node, traits_list)
    return nodes.create_call_node_s(node, lang_names.EXTEND, [typename_1_arg, traits_2_arg])


def simplify_trait(compiler, code, node):
    trait_name_node = node_first(node)
    var_name_node = node_second(node)
    constraints_node = node_third(node)

    trait_name_1_arg = nodes.create_symbol_node(trait_name_node, trait_name_node)
    var_name_2_arg = nodes.create_symbol_node(trait_name_node, var_name_node)
    constraints_3_arg = constraints_node
    call_node = nodes.create_call_node_s(node, lang_names.TRAIT, [trait_name_1_arg, var_name_2_arg, constraints_3_arg])
    trait_node = nodes.create_assign_node(node, trait_name_node, call_node)

    method_sources = node_fourth(node)
    methods = []

    # First declare methods name. compiler second pass doesn`t walk through calls and assigns
    # Possible fix -> separate ast for simple and complicated assigns NT_ASSIGN, NT_ASSIGN_MATCH
    for method_source in method_sources:
        name_node = method_source[0]
        assign_void = nodes.create_assign_node(name_node, name_node, nodes.create_void_node(name_node))
        methods.append(assign_void)

    for method_source in method_sources:
        trait_1_arg = trait_name_node
        name_node = method_source[0]
        name_2_arg = nodes.create_symbol_node(name_node, name_node)

        sig_3_arg = method_source[1]
        default_impl = method_source[2]

        if nodes.is_empty_node(default_impl):
            impl_4_arg = nodes.create_void_node(name_2_arg)
        else:
            impl_4_arg = nodes.create_fun_node(name_2_arg, nodes.empty_node(), default_impl)

        method_call_node = nodes.create_call_node_s(node,
                                                    lang_names.METHOD,
                                                    [trait_1_arg, name_2_arg, sig_3_arg, impl_4_arg])
        assign_node = nodes.create_assign_node(node, name_node, method_call_node)
        methods.append(assign_node)
    return trait_node, nodes.list_node(methods)
