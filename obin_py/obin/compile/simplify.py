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
