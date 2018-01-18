from lalan.compile.parse.nodes import (node_type, node_arity,
                                       node_first, node_second, node_third, node_fourth, node_fifth, node_children,
                                       is_empty_node)
from lalan.runtime import error
from lalan.types import space, api, plist, environment, symbol as symbols, string as strings
from lalan.builtins import lang_names

from lalan.compile.parse import nodes, node_type as nt


def simplify_error(compiler, code, node, message):
    from lalan.compile.compiler import compile_error
    return compile_error(compiler, code, node, message)


def simplify_type(compiler, code, node):
    name_node = node_first(node)
    fields = node_second(node)

    name_1_arg = nodes.create_symbol_node(name_node, name_node)
    if is_empty_node(fields):
        fields_2_arg = nodes.create_empty_list_node(node)
    else:
        fields_2_arg = nodes.create_list_node_from_list(node, fields)

    call_node = nodes.create_call_node_s(node, lang_names.TYPE, [name_1_arg, fields_2_arg])
    return nodes.create_assign_node(node, name_node, call_node)


def simplify_let(compiler, code, node):
    let_block = node_first(node)
    in_block = node_second(node)
    body = plist.concat(let_block, in_block)
    func = nodes.create_fun_0_node(node, nodes.empty_node(), body)
    return nodes.create_call_node_1(node, func, nodes.create_unit_node(node))


def simplify_not(compiler, code, node):
    left = node_first(node)
    return nodes.create_not_call(node, left)


def simplify_cons(compiler, code, node):
    left = node_first(node)
    right = node_second(node)
    return nodes.create_cons_call(node, left, right)


def simplify_delay(compiler, code, node):
    exp = node_first(node)
    fun_1_arg = nodes.create_fun_0_node(node, nodes.empty_node(), nodes.list_node([exp]))
    return nodes.create_call_node_s(node, lang_names.DELAY, [fun_1_arg])


def simplify_extend(compiler, code, node):
    typename_1_arg = node_first(node)
    mixins = node_second(node)
    methods = node_third(node)
    lets = node_fourth(node)
    overrides = node_fifth(node)

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

    for method_data in lets:
        generic_name = method_data[0]
        impl = method_data[1]
        methods_list.append(
            nodes.create_tuple_node(generic_name, [
                generic_name,
                impl
            ])
        )

    for method_data in overrides:
        generic_name = method_data[0]
        impl = method_data[1]
        func = nodes.create_fun_node(generic_name, nodes.empty_node(), impl)
        wrapper = nodes.create_fun_1_node(
            generic_name, nodes.empty_node(),
            nodes.create_name_node_s(generic_name, lang_names.SUPER_NAME),
            func
        )
        call_override = nodes.create_call_node_s(node, lang_names.OVERRIDE, [generic_name, typename_1_arg, wrapper])
        methods_list.append(
            nodes.create_tuple_node(generic_name, [
                generic_name,
                call_override
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

    mixins_node = node_third(node)
    mixins_arg = nodes.create_list_node_from_list(node, mixins_node)
    call_node = nodes.create_call_node_s(node, lang_names.INTERFACE, [name_1_arg, generics_2_arg, mixins_arg])
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
        if nodes.node_type(method_source) == nt.NT_ASSIGN:
            generic_node = nodes.node_first(method_source)
            impl = nodes.node_second(method_source)
            methods.append(
                nodes.create_tuple_node(generic_node, [
                    generic_node,
                    impl
                ])
            )
        else:
            generic_node = nodes.node_first(method_source)
            impl = nodes.node_second(method_source)

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
