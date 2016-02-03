from obin.compile.parse import tokens
from obin.compile.parse import token_type as tt
from obin.compile.parse import node_type as nt
from obin.types import space, api


def __newnode(ntype, token, children):
    if children is not None:
        for child in children:
            if not is_node(child):
                print child
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
    return space.newnil()


def is_empty_node(n):
    return space.isnil(n)


def list_node(items):
    for item in items:
        assert is_node(item)
    return space.newlist(items)


def is_list_node(node):
    return space.islist(node)


def is_node(node):
    return space.islist(node) or space.istuple(node) or space.isnil(node)


def node_blank(token):
    return __newnode(-1, token, None)


def node_0(ntype, token):
    return __newnode(ntype, token, None)


def node_1(ntype, token, child):
    return __newnode(ntype, token, [child])


def node_2(ntype, token, child1, child2):
    return __newnode(ntype, token, [child1, child2])


def node_3(ntype, token, child1, child2, child3):
    return __newnode(ntype, token, [child1, child2, child3])


def node_4(ntype, token, child1, child2, child3, child4):
    return __newnode(ntype, token, [child1, child2, child3, child4])


def node_type(node):
    return api.to_i(api.at_index(node, 0))


def node_token(node):
    return api.at_index(node, 1)


def node_children(node):
    return api.at_index(node, 2)


def node_token_type(node):
    return tokens.token_type(node_token(node))


def node_arity(node):
    return api.n_length(node_children(node))


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


def node_to_d(node):
    if is_empty_node(node):
        return "{ EmptyNode:'EmptyNode' }"
    elif is_list_node(node):
        return [node_to_d(child) for child in node]
    else:
        d = {"_type": tokens.token_type_to_str(node_token_type(node)),
             "_ntype": nt.node_type_to_str(node_type(node)) if node_type(node) != -1 else "",
             "_value": node_value(node),
             "_line": api.to_i(node_line(node))
             }

        if not api.isempty(node_children(node)):
            d['children'] = [node_to_d(child) for child in node_children(node)]

        return d


def node_to_string(node):
    import json
    d = node_to_d(node)
    return space.newstring_from_str(json.dumps(d, sort_keys=True,
                                               indent=2, separators=(',', ': ')))


def create_token_from_node(type, value, node):
    return tokens.newtoken(type, value, node_position(node), node_line(node), node_column(node))


def create_name_node(basenode, name):
    return node_0(nt.NT_NAME, create_token_from_node(tt.TT_NAME, name, basenode))


def create_str_node(basenode, strval):
    return node_0(nt.NT_STR, create_token_from_node(tt.TT_STR, strval, basenode))


def create_symbol_node(basenode, name):
    return node_1(nt.NT_SYMBOL, create_token_from_node(tt.TT_COLON, ":", basenode), name)


def create_int_node(basenode, val):
    return node_0(nt.NT_INT, create_token_from_node(tt.TT_INT, str(val), basenode))


def create_true_node(basenode):
    return node_0(nt.NT_TRUE, create_token_from_node(tt.TT_TRUE, "true", basenode))


def create_nil_node(basenode):
    return node_0(nt.NT_NIL, create_token_from_node(tt.TT_NIL, "nil", basenode))


def create_goto_node(label):
    return node_0(nt.NT_GOTO,
                  tokens.newtoken(tt.TT_GOTO, str(label), space.newint(-1), space.newint(-1), space.newint(-1)))


def create_wildcard_node(basenode):
    return node_0(nt.NT_WILDCARD, create_token_from_node(tt.TT_WILDCARD, "_", basenode))


def create_tuple_node(basenode, elements):
    return node_1(nt.NT_TUPLE, create_token_from_node(tt.TT_LPAREN, "(", basenode), list_node(elements))


def create_if_node(basenode, branches):
    return node_1(nt.NT_IF, create_token_from_node(tt.TT_IF, "if", basenode), list_node(branches))


def create_empty_list_node(basenode):
    return node_1(nt.NT_LIST, create_token_from_node(tt.TT_LSQUARE, "[", basenode), list_node([]))


def create_empty_map_node(basenode):
    return node_1(nt.NT_MAP, create_token_from_node(tt.TT_LCURLY, "{", basenode), list_node([]))


def create_call_node(basenode, func, exp):
    return node_2(nt.NT_CALL, create_token_from_node(tt.TT_LPAREN, "(", basenode), func, list_node([exp]))


def create_eq_node(basenode, left, right):
    return node_2(nt.NT_EQ, create_token_from_node(tt.TT_EQ, "==", basenode), left, right)


def create_isnot_node(basenode, left, right):
    return node_2(nt.NT_ISNOT, create_token_from_node(tt.TT_ISNOT, "isnot", basenode), left, right)


def create_is_node(basenode, left, right):
    return node_2(nt.NT_IS, create_token_from_node(tt.TT_IS, "is", basenode), left, right)


def create_in_node(basenode, left, right):
    return node_2(nt.NT_IN, create_token_from_node(tt.TT_IN, "in", basenode), left, right)


def create_and_node(basenode, left, right):
    return node_2(nt.NT_AND, create_token_from_node(tt.TT_AND, "and", basenode), left, right)


def create_assign_node(basenode, left, right):
    return node_2(nt.NT_ASSIGN, create_token_from_node(tt.TT_ASSIGN, "=", basenode), left, right)


def create_slice_til_the_end(basenode):
    first = create_int_node(basenode, "1")
    second = create_wildcard_node(basenode)
    return node_2(nt.NT_RANGE, create_token_from_node(tt.TT_DOUBLE_COLON, "..", basenode), first, second)


def create_lookup_node(basenode, left, right):
    return node_2(nt.NT_LOOKUP, create_token_from_node(tt.TT_LSQUARE, "[", basenode), left, right)


def create_bind_node(basenode, left, right):
    return node_2(nt.NT_BIND, create_token_from_node(tt.TT_AT_SIGN, "@", basenode), left, right)


def create_kindof_node(basenode, left, right):
    return node_2(nt.NT_KINDOF, create_token_from_node(tt.TT_KINDOF, "kindof", basenode), left, right)


def create_try_statement_node(basenode, exp, success, fail):
    return node_3(nt.NT_TRY,
                  create_token_from_node(tt.TT_TRY, "try", basenode),
                  list_node([exp, success]),
                  list_node([empty_node(), list_node([fail])]),
                  empty_node())
