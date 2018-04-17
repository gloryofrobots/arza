from arza.runtime import error
from arza.types import api, space


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

    # for reporting ambiguous dispatch errors
    def get_method_node(self):
        return self.nextnode.get_method_node()

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


def extract_signature(process, dag):
    leaf = dag.get_method_node()
    return leaf.signature


def _check_ambiguous_methods(process, args, stack):
    if len(stack) <= 1:
        return

    first = stack[0]
    second = stack[1]
    best_rank = first[1]
    if best_rank != second[1]:
        return

    sig1 = extract_signature(process, first[0])
    errors = [sig1]

    for i in range(1, len(stack)):
        node = stack[i]
        if best_rank != node[1]:
            break
        sig = extract_signature(process, node[0])
        errors.append(sig)

    return error.throw_3(error.Errors.SPECIALIZE_ERROR,
                         space.newstring(u"Ambiguous method resolution"), args, space.newlist(errors))


def evaluate_decision(process, stack, nodes, args):
    for node in nodes:
        rank = node.get_rank(process, args)
        api.d.pbp(10, "rank", rank, node)
        if rank >= 0:
            stack.append((node, rank))
    api.d.pbp(10, ">>before sort", stack, args)
    # print "1", stack
    sort_stack(stack)
    _check_ambiguous_methods(process, args, stack)
    api.d.pbp(10, ">>after sort", stack, args)
    # stack.sort(key=itemgetter(1))
    # print "2", stack
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
    def __init__(self, signature, method):
        self.signature = signature
        self.method = method

    def get_rank(self, process, args):
        return 0

    def get_method_node(self):
        return self

    def evaluate(self, process, args):
        return self.method

    def __str__(self):
        return '[Method]'
