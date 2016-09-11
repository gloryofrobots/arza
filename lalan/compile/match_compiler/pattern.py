from lalan.compile.parse.parser import *
from lalan.types import plist
from lalan.compile.parse.nodes import *
from lalan.types import space, api
from lalan.misc import platform, strutil
from transform_state import *

# this file created only for one function get_pattern_names
# function get_pattern_names used in managing when guards in def statement


###################################################################################
###################################################################################

def add_assign(names, name):
    return plist.cons(name, names)


def _process_tuple(state, pattern, patterns):

    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    if count_i == 0:
        return _process_unit(state, pattern, patterns)

    last_index = count_i - 1

    patterns = add_assign(patterns, ["is_indexed", _create_path_node(pattern)])

    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        patterns = add_assign(patterns, ["length_ge", _create_path_node(pattern), count])
    else:
        patterns = add_assign(patterns, ["length", _create_path_node(pattern), count])

    if last_index > 0:
        for i, child in enumerate(children[0:last_index]):
            # TODO MOVE TO PARSER
            if node_type(child) == NT_REST:
                return transform_error(state, child, u'Invalid use of ... in tuple pattern')

            patterns = _get_pattern_assigns(state, child, patterns,
                                        add_path(create_int_node(child, i)))
    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        cur_slice = create_drop_node(last_child, create_int_node(last_child, last_index))
        patterns = _get_pattern_assigns(state, last_child, patterns, add_path(cur_slice))
    else:
        patterns = _get_pattern_assigns(state, last_child, patterns,
                                    add_path(create_int_node(last_child, last_index)))

    return patterns


def _process_unit(state, pattern, patterns):
    patterns = add_assign(patterns, ["equal", _create_path_node(pattern), create_unit_node(pattern)])
    return patterns


def _on_cons(state, pattern, patterns):
    patterns = add_assign(patterns, ["is_seq", _create_path_node(pattern)])
    head = nodes.node_first(pattern)
    tail = nodes.node_second(pattern)
    patterns = add_assign(patterns, ["is_not_empty", _create_path_node(pattern)])

    head_path = add_path(create_head_node(head))
    patterns = _get_pattern_assigns(state, head, patterns, head_path)

    tail_path = add_path(create_tail_node(tail))
    patterns = _get_pattern_assigns(state, tail, patterns, tail_path)
    return patterns


def _on_list(state, pattern, patterns):
    patterns = add_assign(patterns, ["is_seq", _create_path_node(pattern)])

    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    # list_length will not be calculated, we need this node for branch merge checker
    # so [a,b] and [a,b,c] didn`t cause the error
    patterns = add_assign(patterns, ["list", _create_path_node(pattern), count])

    if count_i == 0:
        return add_assign(patterns, ["is_empty", _create_path_node(pattern)])

    # first process all args except last which might be ...rest param
    last_index = count_i - 1
    cur_path = path
    if last_index > 0:
        for i, child in enumerate(children[0:last_index]):
            if node_type(child) == NT_REST:
                return transform_error(state, child, u'Invalid use of Rest')

            patterns = add_assign(patterns, ["is_not_empty", _create_path_node(pattern, cur_path)])

            child_path = add_path(create_head_node(child), cur_path)
            cur_slice = create_tail_node(child)
            cur_path = add_path(cur_slice, cur_path)
            patterns = _get_pattern_assigns(state, child, patterns, child_path)

    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        child_path = cur_path
        patterns = _get_pattern_assigns(state, last_child, patterns, child_path)
    else:
        patterns = add_assign(patterns, ["is_not_empty", _create_path_node(pattern, cur_path)])
        child_path = add_path(create_head_node(last_child), cur_path)
        # process child
        patterns = _get_pattern_assigns(state, last_child, patterns, child_path)

        # Ensure that list is empty
        # IMPORTANT IT NEED TO BE THE LAST CHECK, OTHERWISE CACHED VARIABLES WILL NOT INITIALIZE
        last_slice = create_tail_node(last_child)
        last_path = add_path(last_slice, cur_path)
        return add_assign(patterns, ["is_empty", _create_path_node(pattern, last_path)])
    return patterns


def _get_map_symbol(key_node):
    key_type = node_type(key_node)
    if key_type == NT_NAME:
        return node_value_s(key_node)
    elif key_type == NT_SYMBOL:
        return node_value_s(node_first(key_node))
    elif key_type == NT_STR:
        return strutil.unquote_s(node_value_s(key_node))


def _on_map(state, pattern, patterns):
    patterns = add_assign(patterns, ["is_map", _create_path_node(pattern)])
    children = node_first(pattern)
    count = len(children)
    # empty map
    if count == 0:
        patterns = add_assign(patterns, ["equal", _create_path_node(pattern), create_empty_map_node(pattern)])
        return patterns

    items = []
    symbols = []
    for child in children:
        key_node = child[0]
        key_value = child[1]

        key_type = node_type(key_node)

        if key_type == NT_NAME:
            key = create_symbol_node(key_node, key_node)
            var_name = key_node
            sym = _get_map_symbol(key_node)
        elif key_type == NT_SYMBOL:
            key = key_node
            var_name = empty_node()
            sym = _get_map_symbol(key_node)
        elif key_type == NT_STR:
            key = key_node
            var_name = empty_node()
            sym = _get_map_symbol(key_node)
        elif key_type == NT_BIND:
            key = node_second(key_node)
            var_name = node_first(key_node)
            sym = _get_map_symbol(key)
        elif key_type == NT_OF:
            key_node_first = node_first(key_node)
            key = create_symbol_node(key_node_first, key_node_first)
            var_name = key_node
            sym = _get_map_symbol(key)
        else:
            assert False

        symbols.append(sym)
        items.append(((key, var_name), key_value))
    # symbols used for in chains and grouping maps in matches
    # TODO implement sorting for symbols amd maps
    symbols = [space.newstring_s(symbol) for symbol in sorted(symbols)]

    patterns = add_assign(patterns, ["map", space.newlist(symbols), _create_path_node(pattern)])

    for item in items:
        symbol_key, varname = item[0]
        key_value = item[1]
        child_path = add_path(symbol_key)
        if not is_empty_node(varname):
            patterns = _get_pattern_assigns(state, varname, patterns, child_path)
        if not is_empty_node(key_value):
            patterns = _get_pattern_assigns(state, key_value, patterns, child_path)

    return patterns


def _on_bind(state, pattern, patterns):
    name = nodes.node_first(pattern)
    exp = nodes.node_second(pattern)
    patterns = add_assign(patterns, ["assign", name, _create_path_node(exp)])
    patterns = _get_pattern_assigns(state, exp, patterns)
    return patterns


def _on_name(state, pattern, patterns):
    add_assign(patterns, pattern)
    patterns = add_assign(patterns, ["assign", pattern, _create_path_node(pattern)])
    return patterns


def _on_wildcard(state, pattern, patterns):
    patterns = add_assign(patterns, ["wildcard"])
    return patterns


def _on_of(pattern, patterns):
    element = node_first(pattern)
    trait = node_second(pattern)
    patterns = add_assign(patterns, ["kindof", _create_path_node(element), trait])
    patterns = _get_pattern_assigns(element, patterns)
    return patterns


def _on_when_no_else(pattern, patterns):
    pat = node_first(pattern)
    guard = node_second(pattern)
    # REAL BAD THING HERE. FIXES TERRIBLE IMPLEMENTATION OF TREE MERGE.
    # TODO REWRITE ALL COMPILER ENTIRELY
    patterns = add_assign(patterns, ["when_dummy", guard])
    patterns = _get_pattern_assigns(pat, patterns)
    patterns = add_assign(patterns, ["when", guard])
    return patterns


def _process_literal(pattern, patterns):
    patterns = add_assign(patterns, ["equal", _create_path_node(pattern), pattern])
    return patterns


def _get_pattern_assigns(pattern, patterns):
    ntype = node_type(pattern)

    if ntype == NT_TUPLE:
        return _process_tuple(pattern, patterns)
    elif ntype == NT_UNIT:
        return _process_unit(pattern, patterns)
    elif ntype == NT_LIST:
        return _on_list(pattern, patterns)
    elif ntype == NT_MAP:
        return _on_map(pattern, patterns)
    elif ntype == NT_BIND:
        return _on_bind(pattern, patterns)
    elif ntype == NT_CONS:
        return _on_cons(pattern, patterns)
    elif ntype == NT_NAME:
        return _on_name(pattern, patterns)
    elif ntype == NT_OF:
        return _on_of(pattern, patterns)
    elif ntype == NT_WILDCARD:
        return _on_wildcard(pattern, patterns)
    elif ntype == NT_WHEN:
        return _on_when_no_else(pattern, patterns)
    elif ntype in [NT_FALSE, NT_TRUE, NT_FLOAT, NT_INT, NT_STR, NT_CHAR, NT_SYMBOL]:
        return _process_literal(pattern, patterns)
    else:
        transform_error(pattern, u"Invalid pattern syntax")


def get_pattern_assigns(pattern):
    patterns = _get_pattern_assigns(pattern, plist.empty())
    patterns = plist.reverse(patterns)
    return patterns
