__author__ = 'gloryofrobots'
from discriminator import TraitDiscriminator


class Argument(object):
    # return new discriminator for argument or choose existed one

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
        raise NotImplementedError()


class ArgumentTrait(Argument):
    def __init__(self, position, trait):
        self.trait = trait
        self.position = position

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
        return other.__class__ == self.__class__ \
               and other.trait == self.trait \
               and other.position == self.position

    def __repr__(self):
        return str(self.trait)

    def __str__(self):
        return self.__repr__()


class Signature(object):
    def __init__(self, args, method):
        from obin.objects.object_space import newvector
        self.arity = args.length()
        self.args = [ArgumentTrait(i, trait) for i, trait in enumerate(args.values())]
        self.method = method

    def __eq__(self, other):
        return other.args == self.args

    def at(self, index):
        return self.args[index]
