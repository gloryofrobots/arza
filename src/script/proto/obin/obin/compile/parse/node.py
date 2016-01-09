from obin.compile.parse.tokens import token_type_to_str


class BaseNode:
    pass


class EmptyNode(BaseNode):
    def to_json_value(self):
        return "EmptyNode"

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

    def init(self, arity):
        if not arity:
            return

        self.children = [None] * arity
        self.arity = arity

    def setchild(self, index, value):
        assert isinstance(value, BaseNode)
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
        d = {"_type": token_type_to_str(self.type), "_value": self.value, "_line": self.line
             # "arity": self.arity, "pos": self.position
             }

        if self.children:
            d['children'] = self.__children_repr()
            # d['children'] = [child.to_dict() if isinstance(child, Node) else child
            #                         for child in self.children if child is not None]

        return d

    def __repr__(self):
        import json

        d = self.to_json_value()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

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

    def __eq__(self, other):
        if not isinstance(other, NodeList):
            return False
        if self.length() != other.length():
            return False

        for item1, item2 in zip(self.items.other.items):
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

    def __repr__(self):
        import json
        d = self.to_json_value()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

    def __len__(self):
        return len(self.items)

    def append(self, item):
        assert isinstance(item, BaseNode)
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
        if isinstance(o, list):
            raise RuntimeError()
        assert not isinstance(o, list)

    return NodeList(items)


def is_list_node(node):
    return isinstance(node, NodeList)
