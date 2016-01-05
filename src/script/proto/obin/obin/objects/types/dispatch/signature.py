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


class PredicateArgument(Argument):
    def __init__(self, position, predicate):
        Argument.__init__(self, position)
        self.predicate = predicate

    def find_old_discriminator(self, discriminators):
        position = self.position
        predicate = self.predicate
        for d in discriminators:
            if isinstance(d, PredicateDiscriminator) \
                    and d.position == position \
                    and d.predicate is predicate:
                return d

        return None

    def make_discriminator(self):
        return PredicateDiscriminator(self.position, self.predicate)

    def _equal_(self, other):
        if not isinstance(other, PredicateArgument):
            return False
        if other.predicate is self.predicate \
                and other.position == self.position:
            return True
        return False

    def _hash_(self):
        # TODO FIX IT. GIVE RPYTHON SOME HASH TO THINK
        return 1024 + self.position

    def __repr__(self):
        return str(self.predicate)

    def __str__(self):
        return self.__repr__()


class ArgumentAny(Argument):
    def find_old_discriminator(self, discriminators):
        position = self.position
        for d in discriminators:
            if d.__class__ is AnyDiscriminator \
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
        if not isinstance(other, ArgumentAny):
            return False
        return self.position == other.position

    def _hash_(self):
        return 256 + self.position


class ArgumentTrait(Argument):
    def __init__(self, position, trait):
        Argument.__init__(self, position)
        self.trait = trait

    def find_old_discriminator(self, discriminators):
        position = self.position
        trait = self.trait
        for d in discriminators:

            if isinstance(d, TraitDiscriminator) \
                    and d.position == position \
                    and d.trait == trait:
                return d

        return None

    def make_discriminator(self):
        return TraitDiscriminator(self.position, self.trait)

    def _equal_(self, other):
        if other.__class__ is self.__class__ \
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

    def get_argument(self, index):
        raise NotImplementedError()


class Signature(BaseSignature):
    def __init__(self, args, method):
        BaseSignature.__init__(self, method)
        self.args = args
        self.arity = len(args)

    def equal(self, other):
        args1 = self.args
        args2 = other.args
        for i in range(0, len(args1)):
            arg1 = args1[i]
            arg2 = args2[i]
            if not api.n_equal(arg1, arg2):
                return False

        return True

    def get_argument(self, index):
        return self.args[index]


def newsignature(process, args, method):
    from obin.objects import space, api
    arity = api.n_length(args)
    sig_args = []
    traits = process.std.traits

    for i in range(arity):
        trait = api.at_index(args, i)
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

        sig_args.append(arg)

    return Signature(sig_args, method)

def new_base_signature(method):
    return BaseSignature(method)