class DAGNode:
    def evaluate(self, process, args):
        raise NotImplementedError()

    def __str__(self):
        return "<DAGNode>"

    def __repr__(self):
        return self.__str__()


class SingleNode(DAGNode):
    def __init__(self, discriminator, nextnode):
        self.nextnode = nextnode
        self.discriminator = discriminator
        self.is_evaluated = False

    def get_rank(self, process, args):
        return self.discriminator.evaluate(process, args)

    def evaluate(self, process, args):
        rank = self.nextnode.get_rank(process, args)
        if rank < 0:
            return None
        return self.nextnode.evaluate(process, args)

    def __str__(self):
        return '[%s, %s]' % (str(self.discriminator), str(self.nextnode))


def sort_stack(stack):
    length = len(stack)
    while True:
        swapped = False
        for i in xrange(1, length):
            # print "swapped"
            v_x = stack[i]
            v_y = stack[i - 1]
            x = v_x[1]
            y = v_y[1]
            if y > x:
                stack[i] = v_y
                stack[i - 1] = v_x
                swapped = True

        if not swapped:
            break


def evaluate_decision(process, stack, nodes, args):
    for node in nodes:
        rank = node.get_rank(process, args)
        if rank >= 0:
            stack.append((node, rank))
    # print "********************", args
    # print "1", stack
    sort_stack(stack)
    # print "2", stack
    # stack.sort(key=itemgetter(1))
    # print "3", stack

    for ranked_node in stack:
        node = ranked_node[0]
        result = node.evaluate(process, args)

        if result is not None:
            return result
    return None


class GroupNode(DAGNode):
    def __init__(self, discriminator, nodes):
        self.nodes = nodes
        self.discriminator = discriminator
        self.ordering_stack = []
        self.is_evaluated = False

    def get_rank(self, process, args):
        return self.discriminator.evaluate(process, args)

    def evaluate(self, process, args):
        del self.ordering_stack[:]
        return evaluate_decision(process, self.ordering_stack, self.nodes, args)

    def __str__(self):
        return '[%s, %s]' % (str(self.discriminator), str(self.nodes))


class RootNode(DAGNode):
    def __init__(self, nodes, discriminators):
        self.discriminators = discriminators
        self.nodes = nodes
        self.ordering_stack = []

    def evaluate(self, process, args):
        del self.ordering_stack[:]
        result = evaluate_decision(process, self.ordering_stack, self.nodes, args)
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

    def get_rank(self, process, args):
        return 0

    def evaluate(self, process, args):
        return self.method

    def __str__(self):
        return '"Method"'
