from obin.objects import api

class Discriminator:
    def __init__(self, position):
        self.position = position
        self.status = -2000

    def reset(self):
        self.status = -2000

    def evaluate(self, args):
        arg = args.at(self.position)

        if self.status == -2000:
            self.status = self._evaluate(arg)
            # print "STATUS", self.status
            assert self.status != -2000

        return self.status

    def _evaluate(self, arg):
        raise NotImplementedError()

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position

    def __str__(self):
        return "<Discriminator %s %s>" % (str(self.position), str(self.status))


class AnyDiscriminator(Discriminator):
    def __init__(self, position):
        Discriminator.__init__(self, position)

    def _evaluate(self, arg):
        return 1000

    def __str__(self):
        return '"Any"'


class PredicateDiscriminator(Discriminator):
    def __init__(self, position, predicate):
        Discriminator.__init__(self, position)
        self.predicate = predicate

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.trait == self.predicate

    def _evaluate(self, arg):
        # TODO GET RID OF MAGIC NUMBERS
        if self.predicate(arg):
            return 100
        else:
            return -1000

    # def __str__(self):
    #     if self.status is None:
    #         status = '"None"'
    #     else:
    #         status = self.status
    #
    #     return '["%s", %s, %s]' % (str(self.predicate), str(self.position), str(status))
    def __str__(self):
        return '"%s:%s"' % (str(self.position), str(self.predicate))


class TraitDiscriminator(Discriminator):
    def __init__(self, position, trait):
        Discriminator.__init__(self, position)
        self.trait = trait

    def _equal_(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.trait == self.trait

    def _evaluate(self, arg):
        if arg is None:
            print 1
        return api.traits(arg).get_index(self.trait)
        # return api.kindof(arg, self.trait)

    # def __str__(self):
    #     return "<TraitDiscriminator %s %s %s>" % (str(self.position), str(self.trait), str(self.status))

    # def __str__(self):
    #     if self.status is None:
    #         status = '"nil"'
    #     else:
    #         status = self.status
    #
    #     return '["%s", %s, %s]' % (str(self.trait._name_), str(self.position), str(status))

    def __str__(self):
        return '"%s:%s"' % (str(self.position), str(self.trait._name_))
