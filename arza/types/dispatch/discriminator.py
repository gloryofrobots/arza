from arza.types import api

# TODO GET RID OF MAGIC NUMBERS

WEIGHT_NOT_FOUND = -1000
WEIGHT_UNKNOWN = -2000
WEIGHT_ANY = 1000
WEIGHT_FOUND = 0
WEIGHT_INTERFACE = WEIGHT_ANY - 1

class Discriminator:
    def __init__(self, position):
        self.position = position
        self.status = WEIGHT_UNKNOWN

    def reset(self):
        self.status = WEIGHT_UNKNOWN

    def evaluate(self, process, args):
        arg = api.at_index(args, self.position)

        if self.status == WEIGHT_UNKNOWN:
            self.status = self._evaluate(process, arg)
            # print "STATUS", self.status
            assert self.status != WEIGHT_UNKNOWN

        return self.status

    def _evaluate(self, process, arg):
        raise NotImplementedError()

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position

    def __str__(self):
        return "<Discriminator %s %s>" % (str(self.position), str(self.status))


class AnyDiscriminator(Discriminator):
    def __init__(self, position):
        Discriminator.__init__(self, position)

    def _evaluate(self, process, arg):
        # print "ANY DIS"
        return WEIGHT_ANY

    def __str__(self):
        return '"Any"'


class PredicateDiscriminator(Discriminator):
    def __init__(self, position, predicate):
        Discriminator.__init__(self, position)
        self.predicate = predicate

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.predicate == self.predicate

    def _evaluate(self, process, arg):
        # print "PRED DIS", arg
        if self.predicate(arg):
            return WEIGHT_FOUND
        else:
            return WEIGHT_NOT_FOUND

    def __str__(self):
        return '"%s:%s"' % (str(self.position), str(self.predicate))


class InterfaceDiscriminator(Discriminator):
    def __init__(self, position, interface):
        Discriminator.__init__(self, position)
        self.interface = interface

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.interface == self.interface

    def _evaluate(self, process, arg):
        t = api.get_type(process, arg)

        if not api.interface_b(process, arg, self.interface):
            return -1000

        #i = api.get_index(t.interfaces, self.interface)
        i = self.interface.count_generics()

        if i == -1:
            return -1

        # print "INTERFACE DIS", self, arg

        # return i + self.PENALTY
        return WEIGHT_INTERFACE - i

    def __str__(self):
        return '"%s:%s"' % (str(self.position), str(self.interface.name))


class TypeDiscriminator(Discriminator):
    def __init__(self, position, type):
        Discriminator.__init__(self, position)
        self.type = type

    def _equal_(self, other):
        val = other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.type == self.type
        # print "TYPE DIS", self, other
        return val

    def _evaluate(self, process, arg):
        if api.typeof_b(process, arg, self.type):
            return WEIGHT_FOUND
        else:
            return WEIGHT_NOT_FOUND

    def __str__(self):
        return '"%s:%s"' % (str(self.position), str(self.type.name))
