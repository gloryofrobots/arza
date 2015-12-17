__author__ = 'gloryofrobots'
from discriminator import *


class Argument(object):
    # return new discriminator for argument or choose existed one
    def __init__(self, position):
        self.position = position

    def find_old_discriminator(self, discriminators):
        raise NotImplementedError()

    def make_discriminator(self):
        raise NotImplementedError()

    def discriminator(self, discriminators):
        d = self.find_old_discriminator(discriminators)
        if d:
            return d

        d = self.make_discriminator()
        discriminators.append(d)
        return d

    def __eq__(self, other):
        if other.__class__ == self.__class__ \
                and other.position == self.position:
            return True
        return False


class PredicateArgument(Argument):
    def __init__(self, position, predicate):
        super(PredicateArgument, self).__init__(position)
        self.predicate = predicate

    def find_old_discriminator(self, discriminators):
        position = self.position
        predicate = self.predicate
        for d in discriminators:
            if d.__class__ == PredicateDiscriminator \
                    and d.position == position \
                    and d.predicate == predicate:
                return d

        return None

    def make_discriminator(self):
        return PredicateDiscriminator(self.position, self.predicate)

    def __eq__(self, other):
        if other.__class__ == self.__class__ \
                and other.predicate is self.predicate \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.predicate)

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return self.predicate.__hash__()

class ArgumentAny(Argument):
    def find_old_discriminator(self, discriminators):
        position = self.position
        for d in discriminators:
            if d.__class__ == AnyDiscriminator\
                    and d.position == position:
                return d

        return None

    def make_discriminator(self):
        return AnyDiscriminator(self.position)

    def __repr__(self):
        return "Any"

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return hash(self.__class__)


class ArgumentTrait(Argument):
    def __init__(self, position, trait):
        super(ArgumentTrait, self).__init__(position)
        self.trait = trait

    def find_old_discriminator(self, discriminators):
        position = self.position
        trait = self.trait
        for d in discriminators:
            if d.__class__ == TraitDiscriminator \
                    and d.position == position \
                    and d.trait == trait:
                return d

        return None

    def make_discriminator(self):
        return TraitDiscriminator(self.position, self.trait)

    def __eq__(self, other):
        if other.__class__ == self.__class__ \
                and other.trait == self.trait \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.trait)

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return self.trait.__hash__()


class Signature(object):
    def __init__(self, args, method):
        from obin.objects import space
        traits = space.state.traits
        self.arity = args.length()
        self.args = []
        for i, trait in enumerate(args):
            if traits.Any is trait:
                arg = ArgumentAny(i)
            elif traits.Object is trait:
                arg = PredicateArgument(i, space.isobject)
            elif traits.Vector is trait:
                arg = PredicateArgument(i, space.isvector)
            elif traits.String is trait:
                arg = PredicateArgument(i, space.isstring)
            elif traits.Function is trait:
                arg = PredicateArgument(i, space.isfunction)
            elif traits.Integer is trait:
                arg = PredicateArgument(i, space.isint)
            elif traits.Float is trait:
                arg = PredicateArgument(i, space.isfloat)
            elif traits.Tuple is trait:
                arg = PredicateArgument(i, space.istuple)
            elif traits.Generic is trait:
                arg = PredicateArgument(i, space.isgeneric)
            elif traits.Nil is trait:
                arg = PredicateArgument(i, space.isnull)
            elif traits.Boolean is trait:
                arg = PredicateArgument(i, space.isboolean)
            else:
                arg = ArgumentTrait(i, trait)

            self.args.append(arg)

        self.method = method

    def __eq__(self, other):
        return other.args == self.args

    def at(self, index):
        return self.args[index]
