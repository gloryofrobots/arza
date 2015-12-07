class SyntaxNode(object):
    def __init__(self, arity):
        self.children = [None] * arity
        self.arity = arity
        self.name = self.__class__.__name__

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

    def __repr__(self):
        return "%s" % (str(self))

class If(SyntaxNode):
    def __init__(self, condition):
        super(If, self).__init__(3)
        self.setfirst(condition)


class Call(SyntaxNode):
    def __init__(self, arg):
        super(Call, self).__init__(1)
        self.setfirst(arg)

class Call(SyntaxNode):
    def __init__(self, arg):
        super(Call, self).__init__(1)
        self.setfirst(arg)
