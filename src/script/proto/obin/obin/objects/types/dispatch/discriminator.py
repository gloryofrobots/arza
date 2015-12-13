class Discriminator(object):
    def __init__(self, position):
        self.position = position
        self.status = None

    def check(self, arg):
        if self.status is None:
            self.status = self._check(arg)
            assert self.status is not None

        return self.status

    def _check(self, arg):
        raise NotImplementedError()

    def __eq__(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position

    def __str__(self):
        return "<Discriminator %s %s>" % (str(self.position), str(self.status))

class TrueDiscriminator(Discriminator):
    def _check(self, arg):
        return True


class TraitDiscriminator(Discriminator):
    def __init__(self, position, trait):
        super(TraitDiscriminator, self).__init__(position)
        self.position = position
        self.trait = trait

    def __eq__(self, other):
        return other.__class__ == self.__class__ \
               and other.position == self.position \
               and other.trait == self.trait

    def _check(self, arg):
        return self.trait.is_attached(arg)

    def __str__(self):
        return "<TraitDiscriminator %s %s %s>" % (str(self.position), str(self.trait), str(self.status))
