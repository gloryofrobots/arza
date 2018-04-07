from arza.compile.parse.parser import *
from arza.types import plist
from arza.compile.parse.nodes import *
from arza.types import space, api
from arza.misc import platform, strutil
from transform_state import *


def _create_path_node(token, path):
    head, tail = plist.split(path)
    if plist.is_empty(tail):
        return head

    return create_lookup_node(token, _create_path_node(token, tail), head)


###################################################################################
###################################################################################

def add_pattern(patterns, args):
    assert isinstance(args, list)
    args[0] = space.newstring_s(args[0])
    return plist.cons(space.newlist(args), patterns)


def empty_pattern(pattern):
    return plist.is_empty(pattern)


def split_patterns(patterns):
    return plist.split(patterns)


def add_path(node, path):
    return plist.cons(node, path)


def _process_tuple(state, pattern, patterns, path):
    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    if count_i == 0:
        return _process_unit(state, pattern, patterns, path)

    last_index = count_i - 1

    patterns = add_pattern(patterns, ["is_tuple", _create_path_node(nodes.node_token(pattern), path)])

    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        min_length = space.newint(last_index)
        patterns = add_pattern(patterns, ["length_ge", _create_path_node(nodes.node_token(pattern), path), min_length])
    else:
        patterns = add_pattern(patterns, ["length", _create_path_node(nodes.node_token(pattern), path), count])

    if last_index > 0:
        for i, child in enumerate(children[0:last_index]):
            # TODO MOVE TO PARSER
            if node_type(child) == NT_REST:
                return transform_error(state, child, u'Invalid use of ... in tuple pattern')

            patterns = _process_pattern(state, child, patterns,
                                        add_path(create_int_node(nodes.node_token(child), i), path))
    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        cur_slice = create_drop_node(nodes.node_token(last_child),
                                     create_int_node(nodes.node_token(last_child), last_index))
        patterns = _process_pattern(state, last_child, patterns, add_path(cur_slice, path))
    else:
        patterns = _process_pattern(state, last_child, patterns,
                                    add_path(create_int_node(nodes.node_token(last_child), last_index), path))

    return patterns


def _process_unit(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["equal",
                                      _create_path_node(nodes.node_token(pattern), path),
                                      create_unit_node(nodes.node_token(pattern))])
    return patterns


def _process_cons(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["is_seq",
                                      _create_path_node(nodes.node_token(pattern), path)])
    head = nodes.node_first(pattern)
    tail = nodes.node_second(pattern)
    patterns = add_pattern(patterns, ["is_not_empty", _create_path_node(nodes.node_token(pattern), path)])

    head_path = add_path(create_head_node(nodes.node_token(head)), path)
    patterns = _process_pattern(state, head, patterns, head_path)

    tail_path = add_path(create_tail_node(nodes.node_token(tail)), path)
    patterns = _process_pattern(state, tail, patterns, tail_path)
    return patterns


def _process_list(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["is_seq", _create_path_node(nodes.node_token(pattern), path)])

    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    # list_length will not be calculated, we need this node for branch merge checker
    # so [a,b] and [a,b,c] didn`t cause the error
    patterns = add_pattern(patterns, ["list", _create_path_node(nodes.node_token(pattern), path), count])

    if count_i == 0:
        return add_pattern(patterns, ["is_empty", _create_path_node(nodes.node_token(pattern), path)])

    # first process all args except last which might be ...rest param
    last_index = count_i - 1
    cur_path = path
    if last_index > 0:
        for i, child in enumerate(children[0:last_index]):
            if node_type(child) == NT_REST:
                return transform_error(state, child, u'Invalid use of Rest')

            patterns = add_pattern(patterns, ["is_not_empty", _create_path_node(nodes.node_token(pattern), cur_path)])

            child_path = add_path(create_head_node(nodes.node_token(child)), cur_path)
            cur_slice = create_tail_node(nodes.node_token(child))
            cur_path = add_path(cur_slice, cur_path)
            patterns = _process_pattern(state, child, patterns, child_path)

    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        child_path = cur_path
        patterns = _process_pattern(state, last_child, patterns, child_path)
    else:
        patterns = add_pattern(patterns, ["is_not_empty", _create_path_node(nodes.node_token(pattern), cur_path)])
        child_path = add_path(create_head_node(nodes.node_token(last_child)), cur_path)
        # process child
        patterns = _process_pattern(state, last_child, patterns, child_path)

        # Ensure that list is empty
        # IMPORTANT IT NEED TO BE THE LAST CHECK, OTHERWISE CACHED VARIABLES WILL NOT INITIALIZE
        last_slice = create_tail_node(nodes.node_token(last_child))
        last_path = add_path(last_slice, cur_path)
        return add_pattern(patterns, ["is_empty", _create_path_node(nodes.node_token(pattern), last_path)])
    return patterns


def _get_map_symbol(key_node):
    key_type = node_type(key_node)
    if key_type == NT_NAME:
        return node_value_s(key_node)
    elif key_type == NT_SYMBOL:
        return node_value_s(node_first(key_node))
    elif key_type == NT_STR:
        return strutil.unquote_s(node_value_s(key_node))


def _process_map(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["is_map", _create_path_node(nodes.node_token(pattern), path)])
    children = node_first(pattern)
    count = len(children)
    # empty map
    if count == 0:
        patterns = add_pattern(patterns, ["equal", _create_path_node(nodes.node_token(pattern), path),
                                          create_empty_map_node(nodes.node_token(pattern))])
        return patterns

    items = []
    symbols = []
    for child in children:
        key_node = child[0]
        key_value = child[1]

        key_type = node_type(key_node)

        if key_type == NT_NAME:
            key = create_symbol_node(nodes.node_token(key_node), key_node)
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
            key = create_symbol_node(nodes.node_token(key_node_first), key_node_first)
            var_name = key_node
            sym = _get_map_symbol(key)
        else:
            assert False

        symbols.append(sym)
        items.append(((key, var_name), key_value))
    # symbols used for in chains and grouping maps in matches
    # TODO implement sorting for symbols amd maps
    symbols = [space.newstring_s(symbol) for symbol in sorted(symbols)]

    patterns = add_pattern(patterns, ["map", space.newlist(symbols),
                                      _create_path_node(nodes.node_token(pattern), path)])

    for item in items:
        symbol_key, varname = item[0]
        key_value = item[1]
        child_path = add_path(symbol_key, path)
        if not is_empty_node(varname):
            patterns = _process_pattern(state, varname, patterns, child_path)
        if not is_empty_node(key_value):
            patterns = _process_pattern(state, key_value, patterns, child_path)

    return patterns


def _process_bind(state, pattern, patterns, path):
    name = nodes.node_first(pattern)
    exp = nodes.node_second(pattern)
    patterns = add_pattern(patterns, ["assign", name,
                                      _create_path_node(nodes.node_token(exp), path)])
    patterns = _process_pattern(state, exp, patterns, path)
    return patterns


def _process_name(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["assign", pattern,
                                      _create_path_node(nodes.node_token(pattern), path)])
    return patterns


def _process_type(state, pattern, patterns, path):
    name = nodes.node_first(pattern)
    patterns = add_pattern(patterns, ["equal",
                                      _create_path_node(nodes.node_token(pattern), path), name])
    return patterns


def _process_interface(state, pattern, patterns, path):
    name = nodes.node_first(pattern)
    patterns = add_pattern(patterns, ["equal",
                                      _create_path_node(nodes.node_token(pattern), path), name])
    return patterns


def _process_wildcard(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["wildcard"])
    return patterns


def _process_of(state, pattern, patterns, path):
    element = node_first(pattern)
    trait = node_second(pattern)
    patterns = add_pattern(patterns, ["kindof",
                                      _create_path_node(nodes.node_token(element), path), trait])
    patterns = _process_pattern(state, element, patterns, path)
    return patterns


def _process_is_implemented(state, pattern, patterns, path):
    element = node_first(pattern)
    trait = node_second(pattern)
    patterns = add_pattern(patterns, ["is_implemented",
                                      _create_path_node(nodes.node_token(element), path), trait])
    patterns = _process_pattern(state, element, patterns, path)
    return patterns


def _process_when_no_else(state, pattern, patterns, path):
    pat = node_first(pattern)
    guard = node_second(pattern)
    # REAL BAD THING HERE. FIXES TERRIBLE IMPLEMENTATION OF TREE MERGE.
    # TODO REWRITE ALL COMPILER ENTIRELY
    patterns = add_pattern(patterns, ["when_dummy", guard])
    patterns = _process_pattern(state, pat, patterns, path)
    patterns = add_pattern(patterns, ["when", guard])
    return patterns


def _process_literal(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["equal",
                                      _create_path_node(nodes.node_token(pattern), path), pattern])
    return patterns


def _process_pattern(state, pattern, patterns, path):
    ntype = node_type(pattern)

    if ntype == NT_TUPLE:
        return _process_tuple(state, pattern, patterns, path)
    elif ntype == NT_UNIT:
        return _process_unit(state, pattern, patterns, path)
    elif ntype == NT_LIST:
        return _process_list(state, pattern, patterns, path)
    elif ntype == NT_MAP:
        return _process_map(state, pattern, patterns, path)
    elif ntype == NT_BIND:
        return _process_bind(state, pattern, patterns, path)
    elif ntype == NT_CONS:
        return _process_cons(state, pattern, patterns, path)
    elif ntype == NT_NAME:
        return _process_name(state, pattern, patterns, path)
    elif ntype == NT_IS_IMPLEMENTED:
        return _process_is_implemented(state, pattern, patterns, path)
    elif ntype == NT_OF:
        return _process_of(state, pattern, patterns, path)
    elif ntype == NT_WILDCARD:
        return _process_wildcard(state, pattern, patterns, path)
    elif ntype == NT_WHEN:
        return _process_when_no_else(state, pattern, patterns, path)
    elif ntype in [NT_FALSE, NT_TRUE, NT_FLOAT, NT_INT, NT_STR, NT_CHAR, NT_SYMBOL, NT_MULTI_STR]:
        return _process_literal(state, pattern, patterns, path)
    else:
        transform_error(state, pattern, u"Invalid pattern syntax")


def process_patterns(state, pattern, path, index):
    patterns = _process_pattern(state, pattern, plist.empty(), path)
    patterns = plist.cons(space.newint(index), patterns)
    patterns = plist.reverse(patterns)

    return patterns
