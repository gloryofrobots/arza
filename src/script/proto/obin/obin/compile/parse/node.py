from obin.compile.parse.tokens import token_type_to_str


class EmptyNode:
    pass


class Node(EmptyNode):
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
        assert isinstance(value, Node) or isinstance(value, NodeList)
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

    def __children_repr(self, nodes):
        children = []
        for child in nodes:
            if isinstance(child, list):
                children.append(self.__children_repr(child))
            elif isinstance(child, Node):
                children.append(child.to_dict())
            else:
                # children.append(child)
                raise ValueError("Node child wrong type", child)

        return children

    def to_dict(self):
        d = {"_type": token_type_to_str(self.type), "_value": self.value, "_line": self.line
             # "arity": self.arity, "pos": self.position
             }

        if self.children:
            d['children'] = self.__children_repr(self.children)
            # d['children'] = [child.to_dict() if isinstance(child, Node) else child
            #                         for child in self.children if child is not None]

        return d

    def __repr__(self):
        import json

        d = self.to_dict()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))


class NodeList(EmptyNode):
    def __init__(self, items):
        assert isinstance(items, list)
        self.items = items

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, item):
        return self.items.__getitem__(item)

    def __len__(self):
        return len(self.items)

    def append(self, item):
        self.items.append(item)

    def append_list(self, items):
        self.items.append(list_node(items))

def empty_node():
    return EmptyNode()


def is_empty_node(n):
    return n.__class__ == EmptyNode

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
