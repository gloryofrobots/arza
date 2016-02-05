from obin.compile.parse.parser import *
from obin.types import plist
from obin.compile.parse.nodes import *
from obin.types import space, api
from obin.utils import misc

class TransformState:
    def __init__(self, process, compiler, code, node):
        self.process = process
        self.compiler = compiler
        self.code = code
        self.node = node

def transform_error(state, node, message):
    from obin.compile.compiler import compile_error
    return compile_error(state.process, state.compiler, state.code, node, message)


def _create_path_node(basenode, path):
    head, tail = plist.split(path)
    if plist.isempty(tail):
        return head

    return create_lookup_node(basenode, _create_path_node(basenode, tail), head)


###################################################################################
###################################################################################

def add_pattern(patterns, args):
    assert isinstance(args, list)
    args[0] = space.newstring_from_str(args[0])
    return plist.prepend(space.newtuple(args), patterns)


def empty_pattern(pattern):
    return plist.isempty(pattern)


def split_patterns(patterns):
    return plist.split(patterns)


def add_path(node, path):
    return plist.prepend(node, path)


def _process_tuple(state, pattern, patterns, path):
    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    last_index = count_i - 1

    patterns = add_pattern(patterns, ["is_indexed", _create_path_node(pattern, path)])

    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        patterns = add_pattern(patterns, ["length_ge", _create_path_node(pattern, path), count])
    else:
        patterns = add_pattern(patterns, ["length", _create_path_node(pattern, path), count])

    if last_index > 0:
        for i, child in enumerate(children[0:last_index]):
            # TODO MOVE TO PARSER
            if node_type(child) == NT_REST:
                return transform_error(state, child, u'Invalid use of ... in tuple pattern')

            patterns = _process_pattern(state, child, patterns,
                                        add_path(create_int_node(child, i), path))
    last_child = children[last_index]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        cur_slice = create_slice_n_end(last_child, create_int_node(last_child, last_index))
        patterns = _process_pattern(state, last_child, patterns, add_path(cur_slice, path))
    else:
        patterns = _process_pattern(state, last_child, patterns,
                                    add_path(create_int_node(last_child, last_index), path))

    # for i, child in enumerate(children):
    #     patterns = _process_pattern(state, child, patterns,
    #                                 add_path(create_int_node(child, i), path))
    return patterns


def _process_list(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["is_seq", _create_path_node(pattern, path)])

    children = node_first(pattern)
    count = api.length(children)
    count_i = api.to_i(count)
    # list_length will not be calculated, we need this node for branch merge checker
    # so [a,b] and [a,b,c] didn`t cause the error
    patterns = add_pattern(patterns, ["list", _create_path_node(pattern, path), count])

    # first process all args except last which might be ...rest param
    cur_path = path
    for i, child in enumerate(children[0:count_i - 1]):
        if node_type(child) == NT_REST:
            return transform_error(state, child, u'Invalid use of Rest')

        patterns = add_pattern(patterns, ["isnot", _create_path_node(pattern, cur_path), create_empty_list_node(child)])

        child_path = add_path(create_int_node(child, 0), cur_path)
        cur_slice = create_slice_1_end(child)
        cur_path = add_path(cur_slice, cur_path)
        patterns = _process_pattern(state, child, patterns, child_path)

    last_child = children[count_i - 1]
    if node_type(last_child) == NT_REST:
        last_child = node_first(last_child)
        child_path = cur_path
        patterns = _process_pattern(state, last_child, patterns, child_path)
    else:
        patterns = add_pattern(patterns,
                               ["isnot", _create_path_node(pattern, cur_path), create_empty_list_node(last_child)])
        child_path = add_path(create_int_node(last_child, 0), cur_path)
        # process child
        patterns = _process_pattern(state, last_child, patterns, child_path)

        # Ensure that list is empty
        # IMPORTANT IT NEED TO BE THE LAST CHECK, OTHERWISE CACHED VARIABLES WILL NOT INITIALIZE
        last_slice = create_slice_1_end(last_child)
        last_path = add_path(last_slice, cur_path)
        patterns = add_pattern(patterns, ["is", _create_path_node(pattern, last_path),
                                          create_empty_list_node(last_child)])
    return patterns


def _get_map_symbol(key_node):
    key_type = node_type(key_node)
    if key_type == NT_NAME:
        return node_value(key_node)
    elif key_type == NT_SYMBOL:
        return node_value(node_first(key_node))
    elif key_type == NT_STR:
        return misc.string_unquote(node_value(key_node))


def _process_map(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["is_map", _create_path_node(pattern, path)])
    children = node_first(pattern)
    count = len(children)
    # empty map
    if count == 0:
        patterns = add_pattern(patterns, ["equal", _create_path_node(pattern, path), create_empty_map_node(pattern)])
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
        else:
            assert False

        symbols.append(sym)
        items.append(((key, var_name), key_value))
    # symbols used for in chains and grouping maps in matches
    # TODO implement sorting for symbols amd maps
    symbols = [space.newstring_from_str(symbol) for symbol in sorted(symbols)]

    patterns = add_pattern(patterns, ["map", space.newlist(symbols), _create_path_node(pattern, path)])

    # for item in items:
    #     symbol_key, varname = item[0]
    #     value = item[1]
    #     child_path = plist.prepend(symbol_key, path)

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
    patterns = add_pattern(patterns, ["assign", name, _create_path_node(exp, path)])
    patterns = _process_pattern(state, exp, patterns, path)
    return patterns


def _process_name(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["assign", pattern, _create_path_node(pattern, path)])
    return patterns


def _process_wildcard(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["wildcard"])
    return patterns


def _process_of(state, pattern, patterns, path):
    element = node_first(pattern)
    trait = node_second(pattern)
    patterns = add_pattern(patterns, ["kindof", _create_path_node(element, path), trait])
    patterns = _process_pattern(state, element, patterns, path)
    return patterns


def _process_literal(state, pattern, patterns, path):
    patterns = add_pattern(patterns, ["equal", _create_path_node(pattern, path), pattern])
    return patterns


def _process_pattern(state, pattern, patterns, path):
    # in case of o-arity case functions
    if is_empty_node(pattern):
        return _process_wildcard(state, pattern, patterns, path)

    ntype = node_type(pattern)

    if ntype == NT_TUPLE:
        return _process_tuple(state, pattern, patterns, path)
    elif ntype == NT_LIST:
        return _process_list(state, pattern, patterns, path)
    elif ntype == NT_MAP:
        return _process_map(state, pattern, patterns, path)
    elif ntype == NT_BIND:
        return _process_bind(state, pattern, patterns, path)
    elif ntype == NT_NAME:
        return _process_name(state, pattern, patterns, path)
    elif ntype == NT_OF:
        return _process_of(state, pattern, patterns, path)
    elif ntype == NT_WILDCARD:
        return _process_wildcard(state, pattern, patterns, path)
    elif ntype in [NT_FALSE, NT_TRUE, NT_FLOAT, NT_INT, NT_NIL, NT_STR, NT_CHAR, NT_SYMBOL]:
        return _process_literal(state, pattern, patterns, path)
    else:
        assert False, ntype


def process_patterns(state, pattern, path, index):
    patterns = _process_pattern(state, pattern, plist.empty(), path)
    patterns = plist.prepend(space.newint(index), patterns)
    patterns = plist.reverse(patterns)
    return patterns


###################################################################################
###################################################################################


def _place_branch_node(tree, head, tail):
    for leaf in tree:
        if api.n_equal(leaf[0], head):
            leaf[1].append(tail)
            return

    tree.append([head, [tail]])


def _group_branches(state, branches):
    groups = []
    for branch in branches:
        head, tail = split_patterns(branch)
        if space.isint(head):
            assert empty_pattern(tail)
            if len(branches) != 1:
                transform_error(state, state.node, u"Invalid match/case transformation: branch overlap")
            groups.append([head, None])
            break
        _place_branch_node(groups, head, tail)

    result = []
    for leaf in groups:
        if space.isint(leaf[0]):
            merged = leaf[1]
        else:
            merged = _group_branches(state, leaf[1])

        result.append((leaf[0], merged))

    return result


def _create_variable_undefs(basenode, variables):
    undefs = [create_assign_node(basenode, var, create_nil_node(basenode)) for var in variables]
    return undefs


def _prepend_to_body(statements, body):
    assert isinstance(statements, list)
    assert space.islist(body)
    # TODO NO MORE ITEMS HERE
    return plist.concat(list_node(statements), body)
    # return list_node(statements + body.items)
    # REMOVE IT LATER
    # if is_list_node(body):
    # else:
    #     return list_node(statements + [body])


###################################################################################
###################################################################################

def _history_get_var(history, exp):
    return exp, []
    # HISTORY DOESN'T WORK WITH MAPS BECAUSE TEMP VARS NOT DEFINES IN NESTED CONDITIONS
    # IF UPPER CONDITION IS GOING FALSE
    # SO I DISABLE IT FOR NOW
    # PROBABLY SOLUTION: BUILD TWO STEP CYCLE. IN FIRST STEP ALL CONDITION ARE INITIALISED,
    # IN SECOND SIDE EFFECTS WILL OCCUR

    # from obin.compile import MATCH_SYS_VAR
    #
    # for record in history:
    #     if api.n_equal(record[0], exp):
    #         return record[1], []
    #
    # name = "%s_%d" % (MATCH_SYS_VAR, len(history))
    # name_node = create_name_node(exp, name)
    # assign = create_assign_node(exp, name_node, exp)
    # history.append((exp, name_node))
    # return name_node, [assign]


def _history_get_condition(history, condition):
    var_name, prefixes = _history_get_var(history, condition)

    new_condition = create_eq_node(condition,
                                   var_name,
                                   create_true_node(condition))

    return new_condition, prefixes


###########################################################################

def transform_body(func, methods, history, node, head, tail, variables):
    next_node, condition, prefixes, new_vars = func(history, head, variables)
    if next_node is None:
        next_node = node

    body, vars = _transform_pattern(next_node, methods, history, new_vars, tail)
    return condition, body, prefixes, vars


def _transform_is_map(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_node(arg_node,
                                create_call_node(arg_node,
                                                 create_name_node(arg_node, "is_map"),
                                                 arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_seq(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_node(arg_node,
                                create_call_node(arg_node,
                                                 create_name_node(arg_node, "is_seq"),
                                                 arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_indexed(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_node(arg_node,
                                create_call_node(arg_node,
                                                 create_name_node(arg_node, "is_indexed"),
                                                 arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_length_ge(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    count = head[2]
    _condition = create_gt_node(arg_node,
                                create_call_node(arg_node,
                                                 create_name_node(arg_node, "length"),
                                                 arg_node),
                                create_int_node(arg_node, str(count)))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_length(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    count = head[2]
    _condition = create_eq_node(arg_node,
                                create_call_node(arg_node,
                                                 create_name_node(arg_node, "length"),
                                                 arg_node),
                                create_int_node(arg_node, str(count)))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_equal(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_eq_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_kindof(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_kindof_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_is(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_is_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


# THIS function creates in chain for maps like if x in $$ and y in $$ and z in $$
def _create_in_and_chain(keys, map_node):
    key, rest = plist.split(keys)
    in_node = create_in_node(map_node,
                             create_symbol_node(map_node,
                                                create_name_node(
                                                    map_node,
                                                    api.to_s(key))),
                             map_node)
    if plist.isempty(rest):
        return in_node

    return create_and_node(map_node, in_node, _create_in_and_chain(rest, map_node))


def _transform_map(history, head, variables):
    right, prefixes = _history_get_var(history, head[2])
    _condition = _create_in_and_chain(head[1], right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return None, condition, prefixes + prefixes1, variables


def _transform_in(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_in_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_isnot(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_isnot_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _is_same_var(var1, var2):
    return node_value(var1) == node_value(var2)


def _transform_assign(history, head, variables):
    left = head[1]
    right, prefixes = _history_get_var(history, head[2])
    if plist.contains_with(variables, left, _is_same_var):
        _condition = create_eq_node(left, left, right)
        condition, prefixes1 = _history_get_condition(history, _condition)
        return left, condition, prefixes + prefixes1, variables
    else:
        prefixes1 = (prefixes + [create_assign_node(left, left, right)])
        return left, None, prefixes1, plist.prepend(left, variables)
        # left = head[1]
        # right = head[2]
        # prefixes = [create_assign_node(left, left, right)]
        # return left, None, prefixes, plist.prepend(left, variables)


def _skip_transform(history, head, variables):
    return None, None, [], variables


TRANSFORM_DISPATCH = {
    "is_indexed": _transform_is_indexed,
    "is_seq": _transform_is_seq,
    "is_map": _transform_is_map,
    "length": _transform_length,
    "length_ge": _transform_length_ge,
    "equal": _transform_equal,
    "assign": _transform_assign,
    "wildcard": _skip_transform,
    "isnot": _transform_isnot,
    "is": _transform_is,
    "in": _transform_in,
    "kindof": _transform_kindof,
    "list": _skip_transform,
    "map": _transform_map,
}


def _transform_pattern(node, methods, history, variables, tree):
    assert isinstance(history, list)
    assert space.islist(variables)

    nodes = []

    vars = plist.empty()

    for branch in tree:
        head = branch[0]
        tail = branch[1]

        if tail is None:
            assert space.isint(head)
            assert len(tree) == 1
            return methods[api.to_i(head)], variables

        dtype = api.to_s(head[0])
        transformer = TRANSFORM_DISPATCH[dtype]

        undefs = plist.substract(vars, variables)
        condition, body, prefixes, vars = \
            transform_body(transformer, methods, history, node, head, tail, variables)

        assert body is not None
        assert prefixes is not None

        if not plist.isempty(undefs):
            undef_nodes = _create_variable_undefs(node, undefs)
            prefixes = undef_nodes + prefixes

        nodes.append((condition, body, prefixes))

    result = []
    for condition, body, prefixes in nodes:
        if condition is None:
            result.append(_prepend_to_body(prefixes, body))
        else:
            if_node = create_if_node(node,
                                     [list_node([condition, body]),
                                      empty_node()])

            result.append(_prepend_to_body(prefixes, list_node([if_node])))

    return list_node(result), vars


def transform(process, compiler, code, node, decisions, decision_node):
    state = TransformState(process, compiler, code, node)
    from obin.compile import MATCH_SYS_VAR
    branches = []
    path = plist.plist1(create_name_node(node, MATCH_SYS_VAR))
    bodies = []

    for pattern in decisions:
        clause = pattern[0]
        body = plist.append(pattern[1], decision_node)
        bodies.append(body)
        index = len(bodies) - 1
        # TODO REMOVE LATER
        assert is_list_node(body)
        # if not is_list_node(body):
        #     body = list_node([body])
        patterns = process_patterns(state, clause, path, index)
        branches.append(patterns)

    tree = _group_branches(state, branches)
    # print tree
    transformed_node, vars = _transform_pattern(node, bodies, [], plist.empty(), tree)
    # print nodes.node_to_string(transformed_node)
    # raise SystemExit()
    return transformed_node
