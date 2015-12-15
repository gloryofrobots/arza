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
        self.ordering_stack = []
        self.is_evaluated = False

    def get_rank(self, args):
        result = self.discriminator.evaluate(args)
        if result is None:
            return None
        return result

    def clear(self):
        if not self.is_evaluated:
            return

        self.ordering_stack[:] = []
        self.is_evaluated = False
        self.discriminator.clear()
        for child in self.nodes:
            child.clear()

    def evaluate(self, args):
        self.is_evaluated = True
        self.ordering_stack[:] = []
        return evaluate_decision(self.nodes, args)

    def __str__(self):
        return "{%s %s}" % (str(self.discriminator), str(self.nodes))


class DAGRoot(DAGNode):
    def __init__(self):
        self.discriminators = []
        self.nodes = []

    def set_nodes(self, nodes):
        self.nodes = nodes

    def evaluate(self, args):
        result = evaluate_decision(self.nodes, args)
        self.clear()
        return result

    def clear(self):
        for child in self.nodes:
            child.clear()

    def __str__(self):
        s = "Dag"
        for i, node in enumerate(self.nodes):
            s += "\n" + str(node)
        s += "\n"
        return s

    def __repr__(self):
        return self.__str__()


class DAGMethodNode(DAGNode):
    def __init__(self, method):
        self.method = method

    def get_rank(self, args):
        return 0

    def clear(self):
        pass

    def evaluate(self, args):
        return self.method

    def __str__(self):
        return "{Method %s}" % (str(self.method._name_))
