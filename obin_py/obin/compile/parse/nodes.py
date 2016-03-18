from obin.compile.parse import tokens
from obin.compile.parse import token_type as tt
from obin.compile.parse import node_type as nt
from obin.types import space, api, plist
from obin.runtime import error
from obin.builtins import lang_names


def newnode(ntype, token, children):
    if children is not None:
        for child in children:
            assert is_node(child), child
        return space.newtuple([
            space.newint(ntype), token, space.newlist(children),
            space.newstring(tt.token_type_to_str(tokens.token_type(token)))
        ])
    else:
        return space.newtuple([
            space.newint(ntype), token, space.newlist([]),
            space.newstring(tt.token_type_to_str(tokens.token_type(token)))
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
    from obin.compile.parse.basic import ParserScope
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


def node_blank(token):
    return newnode(-1, token, None)


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


def node_position(node):
    return tokens.token_position(node_token(node))


def node_line(node):
    return tokens.token_line(node_token(node))


def node_column(node):
    return tokens.token_column(node_token(node))


def is_wildcard_node(n):
    return node_type(n) == nt.NT_WILDCARD

def tuple_node_length(n):
    assert node_type(n) == nt.NT_TUPLE, nt.node_type_to_str(node_type(n))
    return api.length_i(node_first(n))

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
            "_ntype": nt.node_type_to_str(node_type(node)) if node_type(node) != -1 else "",
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


def create_token_from_node(type, value, node):
    return tokens.newtoken(type, value, node_position(node), node_line(node), node_column(node))


def create_function_variants(args, body):
    return list_node([list_node([args, body])])


def create_fun_node(basenode, name, funcs):
    return node_2(nt.NT_FUN, create_token_from_node(tt.TT_STR, "fun", basenode), name, funcs)


def create_temporary_node(basenode, idx):
    return node_1(nt.NT_TEMPORARY, create_token_from_node(tt.TT_UNKNOWN, "", basenode), space.newint(idx))


def create_name_from_operator(basenode, op):
    return create_name_node_s(basenode, node_value_s(op))


def create_name_node_s(basenode, name):
    return node_0(nt.NT_NAME, create_token_from_node(tt.TT_NAME, name, basenode))


def create_name_node(basenode, name):
    return create_name_node_s(basenode, api.to_s(name))


def create_str_node(basenode, strval):
    return node_0(nt.NT_STR, create_token_from_node(tt.TT_STR, strval, basenode))


def create_symbol_node(basenode, name):
    return node_1(nt.NT_SYMBOL, create_token_from_node(tt.TT_SHARP, "#", basenode), name)


def create_symbol_node_s(basenode, name):
    return node_1(nt.NT_SYMBOL, create_token_from_node(tt.TT_SHARP, "#", basenode),
                  create_name_node_s(basenode, name))


def create_int_node(basenode, val):
    return node_0(nt.NT_INT, create_token_from_node(tt.TT_INT, str(val), basenode))


def create_true_node(basenode):
    return node_0(nt.NT_TRUE, create_token_from_node(tt.TT_TRUE, "true", basenode))


def create_undefine_node(basenode, varname):
    return node_1(nt.NT_UNDEFINE, create_token_from_node(tt.TT_UNKNOWN, "undefine", basenode), varname)


def create_goto_node(label):
    return node_0(nt.NT_GOTO,
                  tokens.newtoken(tt.TT_UNKNOWN, str(label), space.newint(-1), space.newint(-1), space.newint(-1)))


def create_fenv_node(basenode):
    return node_0(nt.NT_FENV,
                  create_token_from_node(tt.TT_NAME, "___fenv", basenode))


def create_wildcard_node(basenode):
    return node_0(nt.NT_WILDCARD, create_token_from_node(tt.TT_WILDCARD, "_", basenode))


def create_unit_node(basenode):
    return node_0(nt.NT_UNIT, create_token_from_node(tt.TT_LPAREN, "(", basenode))


# def create_tuple_with_unit_node(basenode):
#     return create_tuple_node(basenode, node_0(nt.NT_UNIT, create_token_from_node(tt.TT_LPAREN, "(", basenode)))

def create_tuple_node(basenode, elements):
    return node_1(nt.NT_TUPLE, create_token_from_node(tt.TT_LPAREN, "(", basenode), list_node(elements))

def create_tuple_node_from_list(basenode, elements):
    assert node_type(elements) == nt.NT_LIST
    items = node_first(elements)
    return node_1(nt.NT_TUPLE, create_token_from_node(tt.TT_LPAREN, "(", basenode), items)

def create_match_fail_node(basenode, val, idx):
    sym = create_symbol_node_s(basenode, val)
    return create_tuple_node(basenode, [sym, create_temporary_node(basenode, idx)])
    # return create_call_node_s(basenode, val, [create_name_node(basenode, var)])


def create_if_node(basenode, branches):
    return node_1(nt.NT_CONDITION, create_token_from_node(tt.TT_IF, "if", basenode), list_node(branches))


def create_list_node(basenode, items):
    return node_1(nt.NT_LIST, create_token_from_node(tt.TT_LSQUARE, "[", basenode), list_node(items))

def create_list_node_from_list(basenode, items):
    return node_1(nt.NT_LIST, create_token_from_node(tt.TT_LSQUARE, "[", basenode), items)

def create_empty_list_node(basenode):
    return node_1(nt.NT_LIST, create_token_from_node(tt.TT_LSQUARE, "[", basenode), list_node([]))


def create_empty_map_node(basenode):
    return node_1(nt.NT_MAP, create_token_from_node(tt.TT_LCURLY, "{", basenode), list_node([]))


def create_call_node(basenode, func, exps):
    return node_2(nt.NT_CALL, create_token_from_node(tt.TT_LPAREN, "(", basenode), func, exps)


def create_call_node_1(basenode, func, exp):
    return node_2(nt.NT_CALL, create_token_from_node(tt.TT_LPAREN, "(", basenode), func, list_node([exp]))


def create_call_node_2(basenode, func, exp1, exp2):
    return node_2(nt.NT_CALL, create_token_from_node(tt.TT_LPAREN, "(", basenode), func, list_node([exp1, exp2]))


def create_call_node_3(basenode, func, exp1, exp2, exp3):
    return node_2(nt.NT_CALL, create_token_from_node(tt.TT_LPAREN, "(", basenode), func, list_node([exp1, exp2, exp3]))


def create_call_node_name(basenode, funcname, exps):
    return create_call_node_s(basenode, api.to_s(funcname), exps)


def create_call_node_s(basenode, funcname, exps):
    return node_2(nt.NT_CALL,
                  create_token_from_node(tt.TT_LPAREN, "(", basenode),
                  create_name_node_s(basenode, funcname),
                  list_node(exps))


def create_when_no_else_node(basenode, cond, body):
    return node_2(nt.NT_WHEN, create_token_from_node(tt.TT_WHEN, "when", basenode), cond, body)


# CALL TO OPERATOR FUNCS
# TODO MAKE IT CONSISTENT WITH OPERATOR REDECLARATION

def create_eq_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.EQ, [left, right])


def create_gt_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.GE, [left, right])


def create_kindof_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.KINDOF, [left, right])


def create_isnot_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.ISNOT, [left, right])


def create_is_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.IS, [left, right])


def create_elem_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.ELEM, [left, right])


def create_is_indexed_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_INDEXED, [val])


def create_is_dict_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_DICT, [val])


def create_is_seq_node(basenode, val):
    return create_call_node_s(basenode, lang_names.IS_SEQ, [val])


def create_len_node(basenode, val):
    return create_call_node_s(basenode, lang_names.LEN, [val])


def create_cons_node(basenode, left, right):
    return create_call_node_s(basenode, lang_names.CONS, [left, right])


##############################

def create_and_node(basenode, left, right):
    return node_2(nt.NT_AND, create_token_from_node(tt.TT_AND, "and", basenode), left, right)


def create_assign_node(basenode, left, right):
    return node_2(nt.NT_ASSIGN, create_token_from_node(tt.TT_ASSIGN, "=", basenode), left, right)


def create_head_node(basenode):
    return node_0(nt.NT_HEAD, create_token_from_node(tt.TT_UNKNOWN, "", basenode))


def create_tail_node(basenode):
    return node_0(nt.NT_TAIL, create_token_from_node(tt.TT_UNKNOWN, "", basenode))


def create_drop_node(basenode, count):
    return node_1(nt.NT_DROP, create_token_from_node(tt.TT_UNKNOWN, "..", basenode), count)


def create_lookup_node(basenode, left, right):
    return node_2(nt.NT_LOOKUP, create_token_from_node(tt.TT_LSQUARE, "[", basenode), left, right)


def create_bind_node(basenode, left, right):
    return node_2(nt.NT_BIND, create_token_from_node(tt.TT_AT_SIGN, "@", basenode), left, right)


def create_of_node(basenode, left, right):
    return node_2(nt.NT_OF, create_token_from_node(tt.TT_OF, "of", basenode), left, right)


def create_match_node(basenode, exp, branches):
    return node_2(nt.NT_MATCH, create_token_from_node(tt.TT_MATCH, "match", basenode), exp, list_node(branches))


def create_try_statement_node(basenode, exp, success, fail):
    return node_3(nt.NT_TRY,
                  create_token_from_node(tt.TT_TRY, "try", basenode),
                  list_node([exp, success]),
                  list_node([empty_node(), list_node([fail])]),
                  empty_node())
