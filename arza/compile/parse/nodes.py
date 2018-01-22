from arza.compile.parse import tokens
from arza.compile.parse import token_type as tt
from arza.compile.parse import node_type as nt
from arza.types import space, api, plist
from arza.runtime import error
from arza.misc import strutil
from arza.builtins import lang_names


def newnode(ntype, token, children):
    assert isinstance(token, tokens.Token)
    if children is not None:
        for child in children:
            if child is None:
                print 1
            assert is_node(child), (child.__class__, child)
        return space.newtuple([
            space.newint(ntype), token, space.newlist(children),
            space.newstring(tt.token_type_to_u(tokens.token_type(token)))
        ])
    else:
        return space.newtuple([
            space.newint(ntype), token, space.newlist([]),
            space.newstring(tt.token_type_to_u(tokens.token_type(token)))
        ])


def empty_node():
    return space.newvoid()


def is_empty_node(n):
    return space.isvoid(n)


def list_node(items):
    assert isinstance(items, list)
    for item in items:
        assert is_node(item), item
    return space.newlist(items)


# TODO THIS IS SILLY IMPLEMENT IT AS WRAPS
def is_list_node(node):
    return space.islist(node)


def is_single_node(node):
    return space.istuple(node) and api.length_i(node) == 4


def is_node(node):
    return space.islist(node) or space.istuple(node) \
           or space.isvoid(node) or is_scope_node(node) or is_int_node(node)


def is_scope_node(node):
    from arza.compile.parse.basic import ParserScope
    return isinstance(node, ParserScope)


def is_int_node(node):
    return space.isint(node)


def node_equal(node1, node2):
    assert is_node(node1) and is_node(node2), (node1, node2)

    if is_list_node(node1) and is_list_node(node2):
        return plist.equal_with(node1, node2, node_equal)

    if is_list_node(node1) or is_list_node(node2):
        return False

    #################################################

    if is_empty_node(node1) and is_empty_node(node2):
        return True

    if is_empty_node(node1) or is_empty_node(node2):
        return False

    #################################################

    if is_int_node(node1) and is_int_node(node2):
        return api.equal_b(node1, node2)

    if is_int_node(node1) or is_int_node(node2):
        return False

    #################################################

    if node_type(node1) != node_type(node2):
        return False

    if node_value_s(node1) != node_value_s(node2):
        return False

    return plist.equal_with(node_children(node1), node_children(node2), node_equal)


def node_0(ntype, token):
    return newnode(ntype, token, None)


def node_1(ntype, token, child):
    return newnode(ntype, token, [child])


def node_2(ntype, token, child1, child2):
    return newnode(ntype, token, [child1, child2])


def node_3(ntype, token, child1, child2, child3):
    return newnode(ntype, token, [child1, child2, child3])


def node_4(ntype, token, child1, child2, child3, child4):
    return newnode(ntype, token, [child1, child2, child3, child4])


def node_type(node):
    return api.to_i(api.at_index(node, 0))


def node_token(node):
    return api.at_index(node, 1)


def node_children(node):
    return api.at_index(node, 2)


def node_token_type(node):
    return tokens.token_type(node_token(node))


def node_arity(node):
    return api.length_i(node_children(node))


def node_getchild(node, index):
    return node_children(node)[index]


def node_first(node):
    return node_getchild(node, 0)


def node_second(node):
    return node_getchild(node, 1)


def node_third(node):
    return node_getchild(node, 2)


def node_fourth(node):
    return node_getchild(node, 3)


def node_value_s(node):
    return tokens.token_value_s(node_token(node))


def node_value(node):
    return tokens.token_value(node_token(node))


def node_length(node):
    return tokens.token_length(node_token(node))


def node_position(node):
    return tokens.token_position(node_token(node))


def node_position_i(node):
    return tokens.token_position_i(node_token(node))


def node_line(node):
    return tokens.token_line(node_token(node))


def node_line_i(node):
    return tokens.token_line_i(node_token(node))


def node_column(node):
    return tokens.token_column(node_token(node))


def list_node_items(n):
    return node_children(n)[0]


def is_wildcard_node(n):
    return node_type(n) == nt.NT_WILDCARD


def is_guarded_pattern(n):
    return node_type(n) == nt.NT_WHEN


def is_equal_pattern(pat1, pat2):
    if is_single_node(pat1) and is_single_node(pat2):
        return node_equal(pat1, pat2)

    return api.equal_b(pat1, pat2)


def pattern_length(n):
    ntype = node_type(n)
    if ntype == nt.NT_WHEN:
        return tuple_node_length(node_first(n))
    return tuple_node_length(n)


def list_node_length(l):
    return api.length_i(node_first(l))


def tuple_node_length(n):
    if node_type(n) == nt.NT_UNIT:
        return 0

    if node_type(n) != nt.NT_TUPLE:
        assert node_type(n) == nt.NT_TUPLE, nt.node_type_to_s(node_type(n))
    return api.length_i(node_first(n))


def int_node_to_int(node):
    value = strutil.string_to_int(node_value_s(node))
    num = space.newnumber(value)
    return num


def imported_name_to_s(node):
    if node_type(node) == nt.NT_IMPORTED_NAME:
        return imported_name_to_s(node_first(node)) + ':' + node_value_s(node_second(node))
    else:
        return node_value_s(node)


def imported_name_to_string(node):
    return space.newstring_s(imported_name_to_s(node))


def make_call_chain(args, func):
    pass


def node_to_d(node):
    if is_empty_node(node):
        return {'empty': True}
    elif is_list_node(node):
        return [node_to_d(child) for child in node]
    elif is_scope_node(node):
        return {'scope': True}
    elif is_int_node(node):
        return {'intValue': api.to_i(node)}
    else:
        d = {
            # "_type": tokens.token_type_to_str(node_token_type(node)),
            "_ntype": nt.node_type_to_s(node_type(node)) if node_type(node) != -1 else "",
            "_value": node_value_s(node),
            # "_line": api.to_i(node_line(node))
        }

        if not api.isempty(node_children(node)):
            d['children'] = [node_to_d(child) for child in node_children(node)]

        return d


def node_to_string(node):
    import json
    d = node_to_d(node)
    return space.newstring_s(json.dumps(d, sort_keys=True,
                                        indent=2, separators=(',', ': ')))


def _find_names(node, names):
    if is_empty_node(node):
        return node
    elif is_list_node(node):
        for c in node:
            _find_names(c, names)
    else:
        ntype = node_type(node)
        if ntype == nt.NT_NAME:
            names.append(node_value(node))
        elif ntype == nt.NT_IMPORTED_NAME:
            names.append(imported_name_to_string(node))
        elif ntype == nt.NT_SYMBOL:
            return
        else:
            children = node_children(node)
            if children is None:
                return

            for c in children:
                _find_names(c, names)


def find_names(node):
    names = []
    _find_names(node, names)
    return plist.plist_unique(names)


# CONSTRUCTORS

def create_token_from_token(type, value, token):
    return tokens.newtoken(type, value,
                           tokens.token_position(token),
                           tokens.token_line(token),
                           tokens.token_column(token), tokens.token_indentation(token))


def create_function_variants(args, exp):
    # print "ARGS", args
    # print "BODY", body
    if not is_list_node(exp):
        body = list_node([exp])
    else:
        body = exp

    return list_node([list_node([
        args, body
    ])])


def create_fun_simple_node(token, name, body):
    return create_fun_node(token, name,
                           create_function_variants(
                               create_tuple_node(token, [create_unit_node(token)]),
                               body))


def create_lambda_node(token, args, exp):
    assert node_type(args) == nt.NT_TUPLE or node_type(args) == nt.NT_UNIT, args
    return node_1(nt.NT_LAMBDA, token,
                  create_function_variants(
                      args,
                      list_node([exp])))


def create_fun_node(token, name, funcs):
    return node_2(nt.NT_FUN, token, name, funcs)


def create_partial_node(token, name):
    return create_call_node_s(token, lang_names.PARTIAL, [name])


def create_temporary_node(token, idx):
    return node_1(nt.NT_TEMPORARY, token, space.newint(idx))


def create_name_from_operator(token, op):
    return create_name_node_s(token, node_value_s(op))


def create_symbol_from_operator(token, op):
    return create_symbol_node(token, create_name_from_operator(token, op))


def create_random_name(token):
    import random
    index = random.random()
    name = "%s_%2.10f" % (lang_names.RANDOM_NAME_PREFIX, index)
    return create_name_node_s(token, name)


def create_name_node_s(token, name):
    return node_0(nt.NT_NAME, create_token_from_token(tt.TT_STR, name, token))


def create_name_node(token, name):
    return create_name_node_s(token, api.to_s(name))


def create_str_node(token, strval):
    return node_0(nt.NT_STR, create_token_from_token(tt.TT_STR, strval, token))


def create_symbol_node(token, name):
    return node_1(nt.NT_SYMBOL, token, name)


def create_symbol_node_string(token, name):
    return node_1(nt.NT_SYMBOL, token,
                  create_name_node(token, name))


def create_symbol_node_s(token, name):
    return node_1(nt.NT_SYMBOL, token,
                  create_name_node_s(token, name))


def create_int_node(token, val):
    return node_0(nt.NT_INT, create_token_from_token(tt.TT_INT, str(val), token))


def create_true_node(token):
    return node_0(nt.NT_TRUE, token)


def create_false_node(token):
    return node_0(nt.NT_FALSE, token)


def create_fargs_node(token):
    return node_0(nt.NT_FARGS, token)


def create_void_node(token):
    return node_0(nt.NT_VOID, token)


def create_undefine_node(token, varname):
    return node_1(nt.NT_UNDEFINE, token, varname)


def create_goto_node(label):
    return node_0(nt.NT_GOTO,
                  tokens.newtoken(tt.TT_UNKNOWN, str(label), space.newint(-1),
                                  space.newint(-1), space.newint(-1),
                                  None))


def create_wildcard_node(token):
    return node_0(nt.NT_WILDCARD, token)


def create_unit_node(token):
    return node_0(nt.NT_UNIT, token)


def create_literal_node(token, node):
    return node_1(nt.NT_LITERAL, token, node)


def create_tuple_node(token, elements):
    return node_1(nt.NT_TUPLE, token, list_node(elements))


def create_tuple_node_from_list(token, elements):
    assert is_list_node(elements)
    return node_1(nt.NT_TUPLE, token, elements)


def create_list_node(token, items):
    return node_1(nt.NT_LIST, token, list_node(items))


def create_list_node_from_list(token, items):
    assert is_list_node(items), items
    return node_1(nt.NT_LIST, token, items)


def create_empty_list_node(token):
    return node_1(nt.NT_LIST, token, list_node([]))


def create_empty_map_node(token):
    return node_1(nt.NT_MAP, token, list_node([]))


def create_match_fail_node(token, val, idx):
    sym = create_symbol_node_s(token, val)
    return create_tuple_node(token, [sym, create_temporary_node(token, idx)])
    # return create_call_node_s(token, val, [create_name_node(token, var)])


def create_if_node(token, branches):
    return node_1(nt.NT_CONDITION, token, list_node(branches))


def create_call_node(token, func, exps):
    return node_2(nt.NT_CALL, token, func, exps)


def create_call_node_1(token, func, exp):
    return node_2(nt.NT_CALL, token, func, list_node([exp]))


def create_call_node_2(token, func, exp1, exp2):
    return node_2(nt.NT_CALL, token, func, list_node([exp1, exp2]))


def create_call_node_3(token, func, exp1, exp2, exp3):
    return node_2(nt.NT_CALL, token, func, list_node([exp1, exp2, exp3]))


def create_call_node_name(token, funcname, exps):
    return create_call_node_s(token, api.to_s(funcname), exps)


def create_call_node_s(token, funcname, exps):
    return node_2(nt.NT_CALL,
                  token,
                  create_name_node_s(token, funcname),
                  list_node(exps))


def create_when_no_else_node(token, cond, body):
    return node_2(nt.NT_WHEN, token, cond, body)


def create_when_node(token, pattern, guard):
    return node_2(nt.NT_WHEN, token, pattern, guard)


# CALL TO OPERATOR FUNCS
# TODO MAKE IT CONSISTENT WITH OPERATOR REDECLARATION

def create_eq_call(token, left, right):
    return create_call_node_s(token, lang_names.EQ, [left, right])


def create_gt_call(token, left, right):
    return create_call_node_s(token, lang_names.GE, [left, right])


def create_kindof_call(token, left, right):
    return create_call_node_s(token, lang_names.KINDOF, [left, right])


def create_is_implemented_call(token, left, right):
    return create_call_node_s(token, lang_names.IS_IMPLEMENTED, [left, right])


def create_isnot_call(token, left, right):
    return create_call_node_s(token, lang_names.ISNOT, [left, right])


def create_is_call(token, left, right):
    return create_call_node_s(token, lang_names.IS, [left, right])


def create_elem_call(token, left, right):
    return create_call_node_s(token, lang_names.ELEM, [left, right])


def create_is_indexed_call(token, val):
    return create_call_node_s(token, lang_names.IS_INDEXED, [val])


def create_is_dict_call(token, val):
    return create_call_node_s(token, lang_names.IS_DICT, [val])


def create_is_empty_call(token, val):
    return create_call_node_s(token, lang_names.IS_EMPTY, [val])


def create_is_seq_call(token, val):
    return create_call_node_s(token, lang_names.IS_SEQ, [val])


def create_len_call(token, val):
    return create_call_node_s(token, lang_names.LEN, [val])


def create_cons_call(token, left, right):
    return create_call_node_s(token, lang_names.CONS, [left, right])


def create_not_call(token, left):
    return create_call_node_s(token, lang_names.NOT, [left])


def create_to_seq_call(token, left):
    return create_call_node_s(token, lang_names.TO_SEQ, [left])


def _create_unpack_call_args(seqs):
    seq = plist.head(seqs)
    rest = plist.tail(seqs)
    if plist.is_empty(rest):
        return seq
    return create_call_node_s(node_token(seq), lang_names.CONCAT, [seq, _create_unpack_call_args(rest)])


def create_unpack_call(token, left, seqs):
    return create_call_node_s(token, lang_names.APPLY, [left, _create_unpack_call_args(seqs)])


##############################

def create_and_node(token, left, right):
    return node_2(nt.NT_AND, token, left, right)


def create_assign_node(token, left, right):
    return node_2(nt.NT_ASSIGN, token, left, right)


def create_head_node(token):
    return node_0(nt.NT_HEAD, token)


def create_tail_node(token):
    return node_0(nt.NT_TAIL, token)


def create_drop_node(token, count):
    return node_1(nt.NT_DROP, token, count)


def create_lookup_node(token, left, right):
    return node_2(nt.NT_LOOKUP, token, left, right)


def create_lookup_index_node(token, left, index):
    return create_lookup_node(token, left, create_int_node(token, index))


def create_bind_node(token, left, right):
    return node_2(nt.NT_BIND, token, left, right)


def create_of_node(token, left, right):
    return node_2(nt.NT_OF, token, left, right)


def create_match_node(token, exp, branches):
    return node_2(nt.NT_MATCH, token, exp, list_node(branches))


def create_try_statement_node(token, exp, success, fail):
    return node_3(nt.NT_TRY,
                  token,
                  list_node([exp, success]),
                  list_node([empty_node(), list_node([fail])]),
                  empty_node())
