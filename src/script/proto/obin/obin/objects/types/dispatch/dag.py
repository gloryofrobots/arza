class DAGNode(object):
    def evaluate(self, args):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

class DecisionNode(DAGNode):
    def __init__(self, discriminator, nodes):
        self.nodes = nodes
        self.discriminator = discriminator

    def add_node(self, node):
        self.nodes.append(node)

    def evaluate(self, args):
        result = self.discriminator.evaluate(args)
        if result is False:
            return False

        for node in self.nodes:
            result = node.evaluate(args)
            if result is not False:
                return result
        return False

    def __str__(self):
        return "{DagNode %s %s}" % (str(self.discriminator), str(self.nodes))

class DAGRoot(DAGNode):
    def __init__(self):
        self.discriminators = []
        self.nodes = []

    def set_nodes(self, nodes):
        self.nodes = nodes

    def add_node(self, node):
        self.nodes.append(node)

    def evaluate(self, args):
        for node in self.nodes:
            result = node.evaluate(args)
            if result is not False:
                return result
        return False

    def __str__(self):
        s = "{DagRoot "
        for node in self.nodes:
            s += "\n" + str(node)
        s += "}"
        return s

    def __repr__(self):
        return self.__str__()

class DAGMethodNode(DAGNode):
    def __init__(self, method):
        self.method = method

    def evaluate(self, args):
        return self.method

    def __str__(self):
        return "{DagMethod %s}" % (str(self.method._name_))
