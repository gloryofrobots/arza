from obin.compile.parse.tokens import token_type_to_str

def is_many(node):
    return isinstance(node, list)


def empty_node():
    return []


def is_empty_node(n):
    return isinstance(n, list) and len(n) == 0


class Node:
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
        assert value is not None
        if isinstance(value, list):
            assert None not in value

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

