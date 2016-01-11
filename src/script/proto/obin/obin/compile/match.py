from obin.compile.parse.parser import *
from obin.objects.types import plist
from obin.compile.parse.node import (is_empty_node,
                                     is_list_node, is_iterable_node, create_assign_node,
                                     create_call_node, create_eq_node,
                                     create_if_node, create_true_node, create_int_node,
                                     create_lookup_node, create_name_node, create_undefined_node)
from obin.objects import space as obs, api

def _create_path_node(basenode, path):
    head, tail = plist.split(path)
    if plist.isempty(tail):
        return head

    return create_lookup_node(basenode, _create_path_node(basenode, tail), head)


def _process_pattern(process, compiler, pattern, stack, path):
    if pattern.type == TT_LPAREN and pattern.arity == 1:
        children = pattern.first()
        count = children.length()
        stack.append(["is_seq", _create_path_node(pattern, path)])
        stack.append(["length", _create_path_node(pattern, path), count])

        for i, child in enumerate(children):
            _process_pattern(process, compiler, child, stack,
                             plist.prepend(create_int_node(child, i), path))
    elif pattern.type == TT_NAME:
        stack.append(["assign", pattern, _create_path_node(pattern, path)])
    elif pattern.type == TT_WILDCARD:
        stack.append(["wildcard"])
    elif pattern.type in [TT_FALSE, TT_TRUE, TT_FLOAT, TT_INT, TT_NIL, TT_STR, TT_CHAR]:
        stack.append(["equal", _create_path_node(pattern, path), pattern])
    else:
        assert False


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

        # print "*******************************"
        # print leaf[0]
        # print leaf[1]

    return result


def _create_variable_undefs(basenode, variables):
    undefs = [create_assign_node(basenode, var, create_undefined_node(basenode)) for var in variables]
    return undefs


def _prepend_to_body(statements, body):
    assert isinstance(statements, list)
    if is_list_node(body):
        return list_node(statements + body.items)
    else:
        return list_node(statements + [body])


def _history_get(history, exp):
    from obin.compile import MATCH_SYS_VAR

    for record in history:
        if api.n_equal(record[0], exp):
            return record[1], []

    name = "%s_%d" % (MATCH_SYS_VAR, len(history))
    name_node = create_name_node(exp, name)
    assign = create_assign_node(exp, name_node, exp)
    history.append((exp, name_node))
    return name_node, [assign]


def _get_history_condition(history, condition):
    var_name, assign = _history_get(history, condition)

    new_condition = create_eq_node(condition,
                                   var_name,
                                   create_true_node(condition))

    return new_condition, assign


def _transform_pattern(process, compiler, node, methods, history, variables, tree):
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

        # init loop state
        type = head[0]
        condition = None
        body = None
        prefixes = None

        undefs = plist.substract(vars, variables)

        if type == "is_seq":
            condition_node = head[1]

            _condition = create_eq_node(condition_node,
                                        create_call_node(condition_node,
                                                         create_name_node(condition_node, "is_seq"),
                                                         condition_node),
                                        create_true_node(condition_node))

            condition, prefixes = _get_history_condition(history, _condition)

            body, vars = _transform_pattern(process, compiler, condition_node, methods, history, variables, tail)
        elif type == "length":
            condition_node = head[1]
            count = head[2]
            _condition = create_eq_node(condition_node,
                                        create_call_node(condition_node,
                                                         create_name_node(condition_node, "length"),
                                                         condition_node),
                                        create_int_node(condition_node, str(count)))

            condition, prefixes = _get_history_condition(history, _condition)
            body, vars = _transform_pattern(process, compiler, condition_node, methods, history, variables, tail)
        elif type == "equal":
            left = head[1]
            right = head[2]
            _condition = create_eq_node(left, left, right)
            condition, prefixes = _get_history_condition(history, _condition)
            body, vars = _transform_pattern(process, compiler, left, methods, history, variables, tail)
        elif type == "assign":
            left = head[1]
            right = head[2]

            condition = None
            # condition = _create_true_node(left)
            body, vars = _transform_pattern(process, compiler, left, methods,
                                            history, plist.prepend(left, variables), tail)
            prefixes = [create_assign_node(left, left, right)]

        elif type == "wildcard":
            condition = None
            # condition = _create_true_node(node)
            prefixes = []
            body, vars = _transform_pattern(process, compiler, node, methods, history, variables, tail)
        else:
            assert False, (head, tail)

        # assert condition is not None
        assert body is not None
        assert prefixes is not None

        if not plist.isempty(undefs):
            undef_nodes = _create_variable_undefs(node, undefs)
            prefixes = prefixes + undef_nodes

        # if len(prefixes) != 0:
        #     body = _prepend_to_body(prefixes, body)

        nodes.append((condition, body, prefixes))
        # nodes.append(list_node([condition, body]))

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
    # ifs = [_create_if_node(node, [success_branch, empty_node()]) for success_branch in nodes]
    # return list_node(ifs), vars


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
    transformed_node, vars = _transform_pattern(process, compiler, node, bodies, [], plist.empty(), tree)
    # print transformed_node
    # raise SystemExit()
    return transformed_node
