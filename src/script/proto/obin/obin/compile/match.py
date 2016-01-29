from obin.compile.parse.parser import *
from obin.types import plist
from obin.compile.parse.nodes import *
from obin.types import space as obs, api
from obin.runtime import error


def match_transform_error(process, compiler, node, message):
    from obin.compile.compiler import info
    return error.throw(error.Errors.COMPILE,
                       obs.newtuple([
                           obs.newtuple(info(node)),
                           obs.newstring(message),
                       ]))


def _create_path_node(basenode, path):
    head, tail = plist.split(path)
    if plist.isempty(tail):
        return head

    return create_lookup_node(basenode, _create_path_node(basenode, tail), head)


###################################################################################
###################################################################################

def _process_tuple(process, compiler, pattern, stack, path):
    children = pattern.first()
    count = children.length()
    stack.append(["is_indexed", _create_path_node(pattern, path)])
    stack.append(["length", _create_path_node(pattern, path), count])

    for i, child in enumerate(children):
        _process_pattern(process, compiler, child, stack,
                         plist.prepend(create_int_node(child, i), path))


def _process_list(process, compiler, pattern, stack, path):
    stack.append(["is_seq", _create_path_node(pattern, path)])

    children = pattern.first()
    count = children.length()
    # list_length doesnt`t calculate we need this node for branch merge checker
    # so [a,b] and [a,b,c] didn`t cause the error
    stack.append(["list", _create_path_node(pattern, path), count])

    # first process all args except last which might be ...rest param
    cur_path = path
    for i, child in enumerate(children[:-1]):
        if child.node_type == NT_REST:
            return match_transform_error(process, compiler, child, u'Invalid use of Rest')

        stack.append(["isnot", _create_path_node(pattern, cur_path), create_empty_list_node(child)])

        child_path = plist.prepend(create_int_node(child, 0), cur_path)
        cur_slice = create_slice_til_the_end(child)
        cur_path = plist.prepend(cur_slice, cur_path)
        _process_pattern(process, compiler, child, stack, child_path)

    last_child = children[-1]
    if last_child.node_type == NT_REST:
        last_child = last_child.first()
        child_path = cur_path
        _process_pattern(process, compiler, last_child, stack, child_path)
    else:
        stack.append(["isnot", _create_path_node(pattern, cur_path), create_empty_list_node(last_child)])
        child_path = plist.prepend(create_int_node(last_child, 0), cur_path)
        # process child
        _process_pattern(process, compiler, last_child, stack, child_path)

        # Ensure that list is empty
        # IMPORTANT IT NEED TO BE THE LAST CHECK, OTHERWISE CACHED VARIABLES WILL NOT INITIALIZE
        last_slice = create_slice_til_the_end(last_child)
        last_path = plist.prepend(last_slice, cur_path)
        stack.append(["is", _create_path_node(pattern, last_path), create_empty_list_node(last_child)])


def _process_map(process, compiler, pattern, stack, path):
    stack.append(["is_map", _create_path_node(pattern, path)])

    children = pattern.first()
    count = children.length()
    # empty map
    if count == 0:
        stack.append(["equal", _create_path_node(pattern, path), create_empty_map_node(pattern)])
        return

    items = []
    symbols = []
    for child in children:
        key = child[0]

        if key.node_type == NT_NAME:
            name = '"%s"' % node_value(key)
            symbols.append(name)
            symbol_key = create_str_node(key, name)
            varname = key
        elif key.node_type == NT_STR:
            symbols.append(node_value(key))
            symbol_key = key
            varname = create_name_node(key, node_value(key))
        else:
            assert False

        value = child[1]

        items.append(((symbol_key, varname), value))

    stack.append(["map", sorted(symbols), _create_path_node(pattern, path)])

    # for item in items:
    #     symbol_key, varname = item[0]
    #     value = item[1]
    #     child_path = plist.prepend(symbol_key, path)

    for item in items:
        symbol_key, varname = item[0]
        value = item[1]
        child_path = plist.prepend(symbol_key, path)
        if is_empty_node(value):
            _process_pattern(process, compiler, varname, stack, child_path)
        else:
            _process_pattern(process, compiler, varname, stack, child_path)
            _process_pattern(process, compiler, value, stack, child_path)


def _process_name(process, compiler, pattern, stack, path):
    stack.append(["assign", pattern, _create_path_node(pattern, path)])


def _process_wildcard(process, compiler, pattern, stack, path):
    stack.append(["wildcard"])


def _process_literal(process, compiler, pattern, stack, path):
    stack.append(["equal", _create_path_node(pattern, path), pattern])


def _process_pattern(process, compiler, pattern, stack, path):
    if pattern.node_type == NT_TUPLE:
        _process_tuple(process, compiler, pattern, stack, path)
    elif pattern.node_type == NT_LIST:
        _process_list(process, compiler, pattern, stack, path)
    elif pattern.node_type == NT_MAP:
        _process_map(process, compiler, pattern, stack, path)
    elif pattern.node_type == NT_NAME:
        _process_name(process, compiler, pattern, stack, path)
    elif pattern.node_type == NT_WILDCARD:
        _process_wildcard(process, compiler, pattern, stack, path)
    elif pattern.node_type in [NT_FALSE, NT_TRUE, NT_FLOAT, NT_INT, NT_NIL, NT_STR, NT_CHAR]:
        _process_literal(process, compiler, pattern, stack, path)
    else:
        assert False


###################################################################################
###################################################################################


def _place_branch_node(tree, head, tail):
    for leaf in tree:
        if leaf[0] == head:
            leaf[1].append(tail)
            return

    tree.append([head, [tail]])


def _group_branches(process, branches):
    groups = []
    for b in branches:
        head = b[0]
        tail = b[1:]
        if isinstance(head, int):
            assert tail == []
            assert len(branches) == 1
            groups.append([head, None])
            break
        _place_branch_node(groups, head, tail)

    result = []
    for leaf in groups:
        if isinstance(leaf[0], int):
            merged = leaf[1]
        else:
            merged = _group_branches(process, leaf[1])

        result.append((leaf[0], merged))

    return result


def _create_variable_undefs(basenode, variables):
    undefs = [create_assign_node(basenode, var, create_nil_node(basenode)) for var in variables]
    return undefs


def _prepend_to_body(statements, body):
    assert isinstance(statements, list)
    if is_list_node(body):
        return list_node(statements + body.items)
    else:
        return list_node(statements + [body])


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


def _transform_is(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_is_node(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _create_in_and_chain(keys, map_node):
    key = keys[0]
    in_node = create_in_node(map_node, create_str_node(map_node, key), map_node)
    if len(keys) == 1:
        return in_node

    return create_and_node(map_node, in_node, _create_in_and_chain(keys[1:], map_node))


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


def _transform_assign(history, head, variables):
    left = head[1]
    right, prefixes = _history_get_var(history, head[2])
    if plist.contains(variables, left):
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
    "equal": _transform_equal,
    "assign": _transform_assign,
    "wildcard": _skip_transform,
    "isnot": _transform_isnot,
    "is": _transform_is,
    "in": _transform_in,
    "list": _skip_transform,
    "map": _transform_map,
}


def _transform_pattern(node, methods, history, variables, tree):
    assert isinstance(history, list)
    assert obs.islist(variables)

    nodes = []

    vars = plist.empty()

    for branch in tree:
        head = branch[0]
        tail = branch[1]

        if tail is None:
            assert isinstance(head, int)
            assert len(tree) == 1
            return methods[head], variables

        type = head[0]
        transformer = TRANSFORM_DISPATCH[type]

        undefs = plist.substract(vars, variables)
        condition, body, prefixes, vars = \
            transform_body(transformer, methods, history, node, head, tail, variables)

        assert body is not None
        assert prefixes is not None

        if not plist.isempty(undefs):
            undef_nodes = _create_variable_undefs(node, undefs)
            prefixes = prefixes + undef_nodes

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


def transform(process, compiler, node, patterns, decision_node):
    from obin.compile import MATCH_SYS_VAR
    branches = []
    path = plist.plist1(create_name_node(node, MATCH_SYS_VAR))
    bodies = []

    for pattern in patterns:
        stack = []
        clause = pattern[0]
        _process_pattern(process, compiler, clause, stack, path)

        body = pattern[1]
        if not is_list_node(body):
            body = list_node([body])

        body.append(decision_node)

        bodies.append(body)
        index = len(bodies) - 1
        stack.append(index)

        branches.append(stack)

    tree = _group_branches(process, branches)
    # print tree
    transformed_node, vars = _transform_pattern(node, bodies, [], plist.empty(), tree)
    # print transformed_node
    # raise SystemExit()
    return transformed_node
