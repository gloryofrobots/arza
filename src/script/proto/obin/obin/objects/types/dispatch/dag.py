class DAGNode(object):
    def evaluate(self, args):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()


def evaluate_decision(nodes, args):
    from operator import itemgetter
    good_nodes = []
    for node in nodes:
        rank = node.get_rank(args)
        if rank is not None:
            good_nodes.append((node, rank))

    ranked_nodes = sorted(good_nodes, key=itemgetter(1))

    for ranked_node in ranked_nodes:
        node = ranked_node[0]
        result = node.evaluate(args)

        if result is not False:
            return result
    return False


class DecisionNode(DAGNode):
    def __init__(self, discriminator, nodes):
        self.nodes = nodes
        self.discriminator = discriminator
        self.rank = None

    def add_node(self, node):
        self.nodes.append(node)

    def get_rank(self, args):
        result = self.discriminator.evaluate(args)
        if result is None:
            return None
        return result

    def evaluate(self, args):
        return evaluate_decision(self.nodes, args)

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
        return evaluate_decision(self.nodes, args)

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

    def get_rank(self, args):
        return 0

    def evaluate(self, args):
        return self.method

    def __str__(self):
        return "{DagMethod %s}" % (str(self.method._name_))
