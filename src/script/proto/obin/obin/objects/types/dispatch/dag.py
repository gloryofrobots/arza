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

def evaluate_decision(nodes, args):
    from operator import itemgetter
    good_nodes = []
    for node in nodes:
        rank = node.get_rank(args)
        if rank != -1:
            good_nodes.append((node, rank))

    ranked_nodes = sorted(good_nodes, key=itemgetter(1))

    for ranked_node in ranked_nodes:
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
        return evaluate_decision(self.nodes, args)

    def __str__(self):
        return '[%s, %s]' % (str(self.discriminator), str(self.nodes))


class RootNode(DAGNode):
    def __init__(self):
        self.discriminators = []
        self.nodes = []

    def set_nodes(self, nodes):
        self.nodes = nodes

    def evaluate(self, args):
        result = evaluate_decision(self.nodes, args)
        self.reset()
        return result

    def reset(self):
        for d in self.discriminators:
            d.reset()

    def __str__(self):
       return "[" + ",\n".join([str(node)  for node in self.nodes]) + "]"


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
