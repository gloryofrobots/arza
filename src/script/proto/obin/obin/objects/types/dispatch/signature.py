__author__ = 'gloryofrobots'
from discriminator import *
from obin.objects.types.root import W_Root


class Argument(W_Root):
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

    def _equal_(self, other):
        if other.__class__ == self.__class__ \
                and other.position == self.position:
            return True
        return False

    def _hash_(self):
        from rpython.rlib.objectmodel import compute_identity_hash
        return compute_identity_hash(self)


class PredicateArgument(Argument):
    def __init__(self, position, predicate):
        Argument.__init__(self, position)
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

    def _equal_(self, other):
        if other.__class__ == self.__class__ \
                and other.predicate is self.predicate \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.predicate)

    def __str__(self):
        return self.__repr__()

    def _hash_(self):
        from rpython.rlib.objectmodel import compute_identity_hash
        return compute_identity_hash(self.predicate)


class ArgumentAny(Argument):
    def find_old_discriminator(self, discriminators):
        position = self.position
        for d in discriminators:
            if d.__class__ == AnyDiscriminator \
                    and d.position == position:
                return d

        return None

    def make_discriminator(self):
        return AnyDiscriminator(self.position)

    def __repr__(self):
        return "Any"

    def __str__(self):
        return self.__repr__()

    def _equal_(self, other):
        return self.__class__ == other.__class__ and self.position == other.position

    def _hash_(self):
        from rpython.rlib.objectmodel import compute_identity_hash
        return compute_identity_hash(self.__class__)


class ArgumentTrait(Argument):
    def __init__(self, position, trait):
        Argument.__init__(self, position)
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

    def _equal_(self, other):
        if other.__class__ == self.__class__ \
                and other.trait == self.trait \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.trait)

    def __str__(self):
        return self.__repr__()

    def _hash_(self):
        return self.trait._hash_()


class BaseSignature:
    def __init__(self, method):
        self.method = method

    def equal(self, other):
        raise NotImplementedError()

    def at(self, index):
        raise NotImplementedError()


class Signature(BaseSignature):
    def __init__(self, args, method):
        BaseSignature.__init__(self, method)

        from obin.objects import space, api
        traits = space.state.traits
        self.arity = args.length()
        self.args = []
        for i in range(self.arity):
            trait = args.at(i)
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

    def equal(self, other):
        for arg1, arg2 in zip(self.args, other.args):
            if not arg1._equal_(arg2):
                return False

        return True

    def at(self, index):
        return self.args[index]
