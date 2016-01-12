from obin.compile.parse.tokens import token_type_to_str
from obin.compile.parse import token_type as tt
from obin.compile.parse import node_type as nt
from obin.objects.types.root import W_Root


class BaseNode(W_Root):
    pass


class EmptyNode(BaseNode):
    def to_json_value(self):
        return "EmptyNode"

    def _equal_(self, other):
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, EmptyNode):
            return False
        return True


class Node(BaseNode):
    def __init__(self, _type, value, position, line):
        self.type = _type
        self.value = value
        self.position = position
        self.line = line
        self.children = None
        self.arity = 0
        self.node_type = None

    def init(self, node_type, arity):
        assert node_type is not None
        self.node_type = node_type

        if arity == 0:
            return

        self.children = [None] * arity
        self.arity = arity

    def setchild(self, index, value):
        if not isinstance(value, BaseNode):
            print type(value)
        assert isinstance(value, BaseNode), value
        self.children[index] = value

    def getchild(self, index):
        return self.children[index]

    def setfirst(self, value):
        self.setchild(0, value)

    def setsecond(self, value):
        self.setchild(1, value)

    def setthird(self, value):
        self.setchild(2, value)

    def setfourth(self, value):
        self.setchild(3, value)

    def first(self):
        return self.getchild(0)

    def second(self):
        return self.getchild(1)

    def third(self):
        return self.getchild(2)

    def fourth(self):
        return self.getchild(3)

    def __children_repr(self):
        return [child.to_json_value() for child in self.children]

    def to_json_value(self):
        d = {"_type": token_type_to_str(self.type),
             "_ntype": nt.node_type_to_str(self.node_type),
             "_value": self.value,
             "_line": self.line
             # "arity": self.arity, "pos": self.position
             }

        if self.children:
            d['children'] = self.__children_repr()
            # d['children'] = [child.to_dict() if isinstance(child, Node) else child
            #                         for child in self.children if child is not None]

        return d

    def _tostring_(self):
        import json

        d = self.to_json_value()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

    def _equal_(self, other):
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.type != other.type:
            return False
        if self.arity != other.arity:
            return False

        if self.arity == 0:
            return self.value == other.value

        for item1, item2 in zip(self.children, other.children):
            res = item1 == item2
            if not res:
                return False
        return True


class NodeList(BaseNode):
    def __init__(self, items):
        assert isinstance(items, list)
        self.items = items

    def _equal_(self, other):
        return self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, NodeList):
            return False
        if self.length() != other.length():
            return False

        for item1, item2 in zip(self.items, other.items):
            if item1 != item2:
                return False
        return True

    def __reversed__(self):
        return reversed(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def length(self):
        return len(self.items)

    def to_json_value(self):
        return [child.to_json_value() for child in self.items]

    def _tostring_(self):
        import json
        d = self.to_json_value()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

    def __len__(self):
        return len(self.items)

    def append(self, item):
        assert isinstance(item, BaseNode), item
        self.items.append(item)

    def append_list(self, items):
        self.items.append(list_node(items))


def empty_node():
    return EmptyNode()


def is_empty_node(n):
    return isinstance(n, EmptyNode)


def is_iterable_node(node):
    return is_list_node(node) and len(node) > 0


def list_node(items):
    assert isinstance(items, list)
    if len(items):
        o = items[0]
        assert not isinstance(o, list)
    for item in items:
        assert isinstance(item, BaseNode)

    return NodeList(items)


def is_list_node(node):
    return isinstance(node, NodeList)

def create_tuple_node(basenode, elements):
    node = Node(tt.TT_LPAREN, "(", basenode.position, basenode.line)
    node.init(nt.NT_TUPLE, 1)
    node.setfirst(list_node(elements))
    return node

def create_call_node(basenode, func, exp):
    node = Node(tt.TT_LPAREN, "(", basenode.position, basenode.line)
    node.init(nt.NT_CALL, 2)
    node.setfirst(func)
    node.setsecond(list_node([exp]))
    return node


def create_if_node(basenode, branches):
    node = Node(tt.TT_IF, "(", basenode.position, basenode.line)
    node.init(nt.NT_IF, 1)
    node.setfirst(list_node(branches))
    return node


def create_eq_node(basenode, left, right):
    node = Node(tt.TT_EQ, "==", basenode.position, basenode.line)
    node.init(nt.NT_EQ, 2)
    node.setfirst(left)
    node.setsecond(right)
    return node


def create_assign_node(basenode, var, exp):
    node = Node(tt.TT_ASSIGN, "=", basenode.position, basenode.line)
    node.init(nt.NT_ASSIGN, 2)
    node.setfirst(var)
    node.setsecond(exp)
    return node


def create_name_node(basenode, name):
    node = Node(tt.TT_NAME, name, basenode.position, basenode.line)
    node.init(nt.NT_NAME, 0)
    return node


def create_int_node(basenode, strval):
    node = Node(tt.TT_INT, strval, basenode.position, basenode.line)
    node.init(nt.NT_INT, 0)
    return node


def create_lookup_node(basenode, left, right):
    node = Node(tt.TT_LSQUARE, "[", basenode.position, basenode.line)
    node.init(nt.NT_LOOKUP, 2)
    node.setfirst(left)
    node.setsecond(right)
    return node


def create_true_node(basenode):
    node = Node(tt.TT_TRUE, "true", basenode.position, basenode.line)
    node.init(nt.NT_TRUE, 0)
    return node


def create_undefined_node(basenode):
    node = Node(tt.TT_UNDEFINED, "undefined", basenode.position, basenode.line)
    node.init(nt.NT_UNDEFINED, 0)
    return node


def create_goto_node(label):
    node = Node(tt.TT_GOTO, label, -1, -1)
    node.init(nt.NT_GOTO, 0)
    return node
