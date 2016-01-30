from obin.compile.parse import tokens
from obin.compile.parse import token_type as tt
from obin.compile.parse import node_type as nt
from obin.types.root import W_Any
from obin.types import space, api


class BaseNode(W_Any):
    pass


class EmptyNode(BaseNode):
    pass

class Node(BaseNode):
    def __init__(self, token):
        self.token = token
        self._children = None
        self._arity = 0
        self._node_type = None


class NodeList(BaseNode):
    def __init__(self, items):
        assert isinstance(items, list)
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)


def node_to_d(node):
    if is_empty_node(node):
        return "{ EmptyNode:'EmptyNode' }"
    elif is_list_node(node):
        return [node_to_d(child) for child in node]
    else:
        d = {"_type": tokens.token_type_to_str(node_token_type(node)),
             "_ntype": nt.node_type_to_str(node_type(node)) if node_type(node) is not None else "",
             "_value": node_value(node),
             "_line": api.to_i(node_line(node))
             # "arity": node.arity, "pos": node.position
             }

        if node._children:
            d['children'] = [node_to_d(child) for child in node._children]
            # d['children'] = [child.to_dict() if isinstance(child, Node) else child
            #                         for child in node.children if child is not None]

        return d


def node_to_string(node):
    import json
    d = node_to_d(node)
    return space.newstring_from_str(json.dumps(d, sort_keys=True,
                      indent=2, separators=(',', ': ')))


def node_init(node, node_type, arity):
    assert node_type is not None
    node._node_type = node_type

    if arity == 0:
        return

    node._children = [None] * arity
    node._arity = arity


def node_setchild(node, index, value):

    # if not isinstance(value, BaseNode):
    #     print type(value)
    assert isinstance(value, BaseNode) or space.islist(value), value
    node._children[index] = value


def node_getchild(node, index):
    return node._children[index]


def node_setfirst(node, value):
    node_setchild(node, 0, value)


def node_setsecond(node, value):
    node_setchild(node, 1, value)


def node_setthird(node, value):
    node_setchild(node, 2, value)


def node_setfourth(node, value):
    node_setchild(node, 3, value)


def node_first(node):
    return node_getchild(node, 0)


def node_second(node):
    return node_getchild(node, 1)


def node_third(node):
    return node_getchild(node, 2)


def node_fourth(node):
    return node_getchild(node, 3)


def node_type(node):
    return node._node_type


def node_arity(node):
    return node._arity


def node_token_type(node):
    return tokens.token_type(node.token)


def node_value(node):
    return tokens.token_value(node.token)


def node_position(node):
    return tokens.token_position(node.token)


def node_line(node):
    return tokens.token_line(node.token)


def node_column(node):
    return tokens.token_column(node.token)


def empty_node():
    return EmptyNode()


def is_empty_node(n):
    return isinstance(n, EmptyNode)


def is_wildcard_node(n):
    return node_type(n) == nt.NT_WILDCARD


def list_node(items):
    return space.newlist(items)
    assert isinstance(items, list)
    for item in items:
        assert isinstance(item, BaseNode)

    return NodeList(items)


def is_list_node(node):
    return space.islist(node)
    return isinstance(node, NodeList)


def create_token_from_node(type, value, node):
    return tokens.newtoken(type, value, node_position(node), node_line(node), node_column(node))


def create_tuple_node(basenode, elements):
    node = Node(create_token_from_node(tt.TT_LPAREN, "(", basenode))
    node_init(node, nt.NT_TUPLE, 1)
    node_setfirst(node, list_node(elements))
    return node


def create_call_node(basenode, func, exp):
    node = Node(create_token_from_node(tt.TT_LPAREN, "(", basenode))
    node_init(node, nt.NT_CALL, 2)
    node_setfirst(node, func)
    node_setsecond(node, list_node([exp]))
    return node


def create_if_node(basenode, branches):
    node = Node(create_token_from_node(tt.TT_IF, "if", basenode))
    node_init(node, nt.NT_IF, 1)
    node_setfirst(node, list_node(branches))
    return node


def create_eq_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_EQ, "==", basenode))
    node_init(node, nt.NT_EQ, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_empty_list_node(basenode):
    node = Node(create_token_from_node(tt.TT_LSQUARE, "[", basenode))
    node_init(node, nt.NT_LIST, 1)
    node_setfirst(node, list_node([]))
    return node


def create_empty_map_node(basenode):
    node = Node(create_token_from_node(tt.TT_LCURLY, "{", basenode))
    node_init(node, nt.NT_MAP, 1)
    node_setfirst(node, list_node([]))
    return node


def create_isnot_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_ISNOT, "isnot", basenode))
    node_init(node, nt.NT_ISNOT, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_is_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_IS, "is", basenode))
    node_init(node, nt.NT_IS, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_in_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_IN, "in", basenode))
    node_init(node, nt.NT_IN, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_and_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_AND, "and", basenode))
    node_init(node, nt.NT_AND, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_assign_node(basenode, var, exp):
    node = Node(create_token_from_node(tt.TT_ASSIGN, "=", basenode))
    node_init(node, nt.NT_ASSIGN, 2)
    node_setfirst(node, var)
    node_setsecond(node, exp)
    return node


def create_name_node(basenode, name):
    node = Node(create_token_from_node(tt.TT_NAME, name, basenode))
    node_init(node, nt.NT_NAME, 0)
    return node


def create_str_node(basenode, strval):
    node = Node(create_token_from_node(tt.TT_STR, strval, basenode))
    node_init(node, nt.NT_STR, 0)
    return node


def create_int_node(basenode, val):
    node = Node(create_token_from_node(tt.TT_INT, str(val), basenode))
    node_init(node, nt.NT_INT, 0)
    return node


def create_lookup_node(basenode, left, right):
    node = Node(create_token_from_node(tt.TT_LSQUARE, "[", basenode))
    node_init(node, nt.NT_LOOKUP, 2)
    node_setfirst(node, left)
    node_setsecond(node, right)
    return node


def create_true_node(basenode):
    node = Node(create_token_from_node(tt.TT_TRUE, "true", basenode))
    node_init(node, nt.NT_TRUE, 0)
    return node


def create_nil_node(basenode):
    node = Node(create_token_from_node(tt.TT_NIL, "nil", basenode))
    node_init(node, nt.NT_NIL, 0)
    return node


def create_slice_til_the_end(basenode):
    node = Node(create_token_from_node(tt.TT_DOUBLE_COLON, "..", basenode))
    node_init(node, nt.NT_RANGE, 2)
    first = create_int_node(basenode, "1")
    second = create_wildcard_node(basenode)
    node_setfirst(node, first)
    node_setsecond(node, second)
    return node


def create_goto_node(label):
    node = Node(tokens.newtoken(tt.TT_GOTO, str(label), space.newint(-1), space.newint(-1), space.newint(-1)))
    node_init(node, nt.NT_GOTO, 0)
    return node


def create_wildcard_node(basenode):
    node = Node(create_token_from_node(tt.TT_WILDCARD, "_", basenode))
    node_init(node, nt.NT_WILDCARD, 0)
    return node


def create_try_statement_node(basenode, exp, success, fail):
    node = Node(create_token_from_node(tt.TT_TRY, "try", basenode))
    node_init(node, nt.NT_TRY, 3)
    node_setfirst(node, list_node([exp, success]))
    node_setsecond(node, list_node([empty_node(), list_node([fail])]))
    node_setthird(node, empty_node())
    return node
