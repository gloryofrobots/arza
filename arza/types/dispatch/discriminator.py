from arza.types import api, space

# TODO GET RID OF MAGIC NUMBERS

WEIGHT_NOT_FOUND = -1000
WEIGHT_UNKNOWN = -2000
WEIGHT_ANY = 1000
WEIGHT_FOUND = 0
WEIGHT_INTERFACE = WEIGHT_ANY - 1
WEIGHT_EMPTY_INTERFACE = -1


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
        return "<D - %s %s>" % (str(self.position), str(self.status))


class AnyDiscriminator(Discriminator):
    def __init__(self, position):
        Discriminator.__init__(self, position)

    def _evaluate(self, process, arg):
        # print "ANY DIS"
        return WEIGHT_ANY

    def __str__(self):
        return '<Any>'


class ValueDiscriminator(Discriminator):
    def __init__(self, position, value):
        Discriminator.__init__(self, position)
        self.value = value

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and api.equal_b(other.value, self.value)

    def _evaluate(self, process, arg):
        # print "PRED DIS", arg
        if api.equal_b(arg, self.value):
            return WEIGHT_FOUND
        else:
            return WEIGHT_NOT_FOUND

    def __str__(self):
        return '<V %s:%s>' % (str(self.position), str(self.value))


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
        return '<P %s:%s>' % (str(self.position), str(self.predicate))


class InterfaceDiscriminator(Discriminator):
    def __init__(self, position, interface):
        Discriminator.__init__(self, position)
        self.interface = interface

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.interface == self.interface

    def _evaluate(self, process, arg):
        t = api.dispatched(process, arg)
        api.d.pbp(10, "type", space.isinterface(arg), t, t.interfaces, t.interfaces_table, self.interface)

        if space.isinterface(arg):
            if api.equal_b(arg, self.interface):
                api.d.pbp(10, "Interface weight")
                return WEIGHT_INTERFACE
            else:
                return WEIGHT_NOT_FOUND

        if not api.interface_b(process, arg, self.interface):
            return WEIGHT_NOT_FOUND

        # i = api.get_index(t.interfaces, self.interface)
        i = self.interface.count_generics()
        api.d.pbp(10, "count gen", i)

        if i == -1:
            return WEIGHT_EMPTY_INTERFACE

        # print "INTERFACE DIS", self, arg

        # return i + self.PENALTY
        # return WEIGHT_INTERFACE - i
        return WEIGHT_INTERFACE

    def __str__(self):
        return '<I - %s:%s>' % (str(self.position), str(self.interface.name))


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
        if space.isabstracttype(arg) and space.isuserdatatype(self.type):
            if api.equal_b(arg, self.type):
                return WEIGHT_FOUND


        _type = api.dispatched(process, arg)
        # n = api.to_s(_type.name)
        i = 0
        while space.isdatatype(_type):
            if api.equal_b(_type, self.type):
                # print "FOUND", i, self.type, _type
                return WEIGHT_FOUND + i
            _type = _type.supertype
            i += 1

        # print "NOTFOUND", self.type, _type
        return WEIGHT_NOT_FOUND

    def __str__(self):
        return '<T - %s:%s>' % (str(self.position), str(self.type.name))
