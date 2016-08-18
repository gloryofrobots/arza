from lalan.compile.parse.parser import *
from lalan.types import plist
from lalan.compile.parse.nodes import *
from lalan.types import space, api
from lalan.misc import platform, strutil
from process import *
from transform_state import *

def _equal_pattern(pat1, pat2):
    if is_single_node(pat1) and is_single_node(pat2):
        return node_equal(pat1, pat2)

    return api.equal_b(pat1, pat2)


def _place_branch_node(tree, head, tail):
    for leaf in tree:
        if plist.equal_with(leaf[0], head, _equal_pattern):
            leaf[1].append(tail)
            return

    tree.append([head, [tail]])


def _group_branches(state, branches):
    groups = []
    for i, branch in enumerate(branches):
        head, tail = split_patterns(branch)
        if space.isint(head):
            assert empty_pattern(tail)
            if len(branches) != 1:
                return transform_error(state, state.node,
                                u"Invalid match/case transformation: at least two branches are overlapped")

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
    return [create_undefine_node(basenode, var) for var in variables]


def _prepend_to_body(statements, body):
    assert isinstance(statements, list)
    assert space.islist(body)
    return plist.concat(list_node(statements), body)


###################################################################################
###################################################################################

def _history_get_var(history, exp):
    return exp, []
    # HISTORY DOESN'T WORK WITH MAPS BECAUSE TEMP VARS NOT DEFINES IN NESTED CONDITIONS
    # IF UPPER CONDITION IS GOING FALSE
    # SO I DISABLE IT FOR NOW
    # PROBABLY SOLUTION: BUILD TWO STEP CYCLE. IN FIRST STEP ALL CONDITION ARE INITIALISED,
    # IN SECOND SIDE EFFECTS WILL OCCUR

    # from lalan.compile import MATCH_SYS_VAR
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

    new_condition = create_eq_call(condition,
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
    _condition = create_is_call(arg_node,
                                create_is_dict_call(arg_node, arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_not_empty(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_call(arg_node,
                                create_is_empty_call(arg_node, arg_node),
                                create_false_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_empty(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_call(arg_node,
                                create_is_empty_call(arg_node, arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_seq(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_call(arg_node,
                                create_is_seq_call(arg_node, arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_is_indexed(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_call(arg_node,
                                create_is_indexed_call(arg_node, arg_node),
                                create_true_node(arg_node))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_length_ge(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    count = head[2]
    _condition = create_gt_call(arg_node,
                                create_len_call(arg_node, arg_node),
                                create_int_node(arg_node, str(count)))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_length(history, head, variables):
    arg_node, prefixes = _history_get_var(history, head[1])
    count = head[2]
    _condition = create_eq_call(arg_node,
                                create_len_call(arg_node, arg_node),
                                create_int_node(arg_node, str(count)))

    condition, prefixes1 = _history_get_condition(history, _condition)
    return arg_node, condition, prefixes + prefixes1, variables


def _transform_equal(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_eq_call(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_when(history, head, variables):
    guard_node, prefixes = _history_get_var(history, head[1])
    _condition = create_is_call(guard_node,
                                guard_node,
                                create_true_node(guard_node))
    condition, prefixes1 = _history_get_condition(history, _condition)
    return guard_node, condition, prefixes + prefixes1, variables


def _transform_kindof(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_kindof_call(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_is(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_is_call(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


# THIS function creates in chain for maps like if x in $$ and y in $$ and z in $$
def _create_in_and_chain(keys, map_node):
    key, rest = plist.split(keys)
    in_node = create_elem_call(map_node,
                               create_symbol_node(map_node,
                                                  create_name_node_s(
                                                      map_node,
                                                      api.to_s(key))),
                               map_node)
    if plist.is_empty(rest):
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
    _condition = create_elem_call(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _transform_isnot(history, head, variables):
    left, prefixes = _history_get_var(history, head[1])
    right = head[2]
    _condition = create_isnot_call(left, left, right)
    condition, prefixes1 = _history_get_condition(history, _condition)
    return left, condition, prefixes + prefixes1, variables


def _is_same_var(var1, var2):
    return node_value_s(var1) == node_value_s(var2)


def _transform_assign(history, head, variables):
    left = head[1]
    right, prefixes = _history_get_var(history, head[2])
    if plist.contains_with(variables, left, _is_same_var):
        _condition = create_eq_call(left, left, right)
        condition, prefixes1 = _history_get_condition(history, _condition)
        return left, condition, prefixes + prefixes1, variables
    else:
        prefixes1 = (prefixes + [create_assign_node(left, left, right)])
        return left, None, prefixes1, plist.cons(left, variables)
        # left = head[1]
        # right = head[2]
        # prefixes = [create_assign_node(left, left, right)]
        # return left, None, prefixes, plist.prepend(left, variables)


def _skip_transform(history, head, variables):
    return None, None, [], variables


TRANSFORM_DISPATCH = {
    "is_empty": _transform_is_empty,
    "is_not_empty": _transform_is_not_empty,
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
    "when": _transform_when,
    "when_dummy": _skip_transform,
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
            # assert len(tree) == 1
            return methods[api.to_i(head)], variables

        dtype = api.to_s(head[0])
        transformer = TRANSFORM_DISPATCH[dtype]

        undefs = plist.substract(vars, variables)
        condition, body, prefixes, vars = \
            transform_body(transformer, methods, history, node, head, tail, variables)

        assert body is not None
        assert prefixes is not None

        if not plist.is_empty(undefs):
            undef_nodes = _create_variable_undefs(node, undefs)
            prefixes = undef_nodes + prefixes

        nodes.append((condition, body, prefixes))

    result = []
    for condition, body, prefixes in nodes:
        if condition is None:
            result.append(_prepend_to_body(prefixes, body))
        else:
            cond_node = create_when_no_else_node(node, condition, body)

            result.append(_prepend_to_body(prefixes, list_node([cond_node])))

    return list_node(result), vars


def transform(compiler, code, node, decisions, decision_node, temp_idx):
    state = TransformState(compiler, code, node)
    branches = []
    path = plist.plist1(create_temporary_node(node, temp_idx))
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