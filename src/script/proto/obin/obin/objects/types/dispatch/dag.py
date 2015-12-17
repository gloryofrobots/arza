class DAGNode(object):
    def evaluate(self, args):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()


class SingleNode(DAGNode):
    def __init__(self, discriminator, nextnode):
        self.nextnode = nextnode
        self.discriminator = discriminator
        self.is_evaluated = False

    def get_rank(self, args):
        return self.discriminator.evaluate(args)

    def evaluate(self, args):
        rank = self.nextnode.get_rank(args)
        if rank == -1:
            return False
        return self.nextnode.evaluate(args)

    def __str__(self):
        return '[%s, %s]' % (str(self.discriminator), str(self.nextnode))


def evaluate_decision(stack, nodes, args):
    from operator import itemgetter
    for node in nodes:
        rank = node.get_rank(args)
        if rank != -1:
            stack.append((node, rank))

    stack.sort(key=itemgetter(1))

    for ranked_node in stack:
        node = ranked_node[0]
        result = node.evaluate(args)

        if result is not False:
            return result
    return False


class GroupNode(DAGNode):
    def __init__(self, discriminator, nodes):
        self.nodes = nodes
        self.discriminator = discriminator
        self.ordering_stack = []
        self.is_evaluated = False

    def get_rank(self, args):
        return self.discriminator.evaluate(args)

    def evaluate(self, args):
        self.ordering_stack[:] = []
        return evaluate_decision(self.ordering_stack, self.nodes, args)

    def __str__(self):
        return '[%s, %s]' % (str(self.discriminator), str(self.nodes))


class RootNode(DAGNode):
    def __init__(self, nodes, discriminators):
        self.discriminators = discriminators
        self.nodes = nodes
        self.ordering_stack = []

    def evaluate(self, args):
        self.ordering_stack[:] = []
        result = evaluate_decision(self.ordering_stack, self.nodes, args)
        self.reset()
        return result

    def reset(self):
        for d in self.discriminators:
            d.reset()

    def __str__(self):
        return "[" + ",\n".join([str(node) for node in self.nodes]) + "]"

    def __repr__(self):
        return self.__str__()


class LeafNode(DAGNode):
    def __init__(self, method):
        self.method = method

    def get_rank(self, args):
        return 0

    def evaluate(self, args):
        return self.method

    def __str__(self):
        return '"Method"'
