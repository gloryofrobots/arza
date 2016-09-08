__author__ = 'gloryofrobots'
from discriminator import *
from lalan.types.root import W_Root
from lalan.types import space, api
from lalan.runtime import error


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


class ArgumentInterface(Argument):
    def __init__(self, position, interface):
        Argument.__init__(self, position)
        self.interface = interface

    def find_old_discriminator(self, discriminators):
        position = self.position
        interface = self.interface
        for d in discriminators:

            if isinstance(d, InterfaceDiscriminator) \
                    and d.position == position \
                    and d.interface == interface:
                return d

        return None

    def make_discriminator(self):
        return InterfaceDiscriminator(self.position, self.interface)

    def _equal_(self, other):
        if other.__class__ is self.__class__ \
                and other.interface == self.interface \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.interface)

    def __str__(self):
        return self.__repr__()

    def _hash_(self):
        return self.interface._hash_()


class ArgumentType(Argument):
    def __init__(self, position, type):
        Argument.__init__(self, position)
        self.type = type

    def find_old_discriminator(self, discriminators):
        position = self.position
        type = self.type
        for d in discriminators:

            if isinstance(d, TypeDiscriminator) \
                    and d.position == position \
                    and d.type == type:
                return d

        return None

    def make_discriminator(self):
        return TypeDiscriminator(self.position, self.type)

    def _equal_(self, other):
        if other.__class__ is self.__class__ \
                and other.type == self.type \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.type)

    def __str__(self):
        return self.__repr__()

    def _hash_(self):
        return self.type._hash_()


class Signature(W_Root):
    def __init__(self, args, method):
        self.method = method
        self.args = args
        self.arity = len(args)

    def _to_string_(self):
        return "<signature %s>" % ", ".join([str(arg) for arg in self.args])

    def equal(self, other):
        args1 = self.args
        args2 = other.args
        for i in range(0, len(args1)):
            arg1 = args1[i]
            arg2 = args2[i]
            if not api.equal_b(arg1, arg2):
                return False

        return True

    def get_argument(self, index):
        return self.args[index]


def _get_interface_predicate(process, interface, index):
    interfaces = process.std.interfaces

    if interfaces.Any is interface:
        arg = ArgumentAny(index)
    else:
        arg = ArgumentInterface(index, interface)

    return arg


def _get_type_predicate(process, _type, index):
    types = process.std.types
    arg = ArgumentType(index, _type)
    # if types.List is _type:
    #     arg = PredicateArgument(index, space.islist)
    # elif types.Tuple is _type:
    #     arg = PredicateArgument(index, space.istuple)
    # elif types.Map is _type:
    #     arg = PredicateArgument(index, space.ispmap)
    # elif types.String is _type:
    #     arg = PredicateArgument(index, space.isstring)
    # elif types.Int is _type:
    #     arg = PredicateArgument(index, space.isint)
    # elif types.Float is _type:
    #     arg = PredicateArgument(index, space.isfloat)
    # elif types.Function is _type:
    #     arg = PredicateArgument(index, space.isfunction)
    # elif types.Generic is _type:
    #     arg = PredicateArgument(index, space.isgeneric)
    # else:
    #     arg = ArgumentType(index, _type)

    return arg


def newsignature(process, args, method):
    arity = api.length_i(args)
    sig_args = []

    for index in range(arity):
        kind = api.at_index(args, index)
        if space.isinterface(kind):
            arg = _get_interface_predicate(process, kind, index)
        elif space.isdatatype(kind):
            arg = _get_type_predicate(process, kind, index)
        else:
            return error.throw_2(error.Errors.TYPE_ERROR,
                                 space.newstring(u"Invalid signature type. Expected type or interface"), kind)

        sig_args.append(arg)

    return Signature(sig_args, method)


