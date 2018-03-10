__author__ = 'gloryofrobots'
from discriminator import *
from arza.types.root import W_Root
from arza.types import space, api, plist
from arza.runtime import error
from arza.compile.parse import nodes
from arza.compile.parse import node_type as nt
from arza.builtins import lang_names


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


class ArgumentValue(Argument):
    def __init__(self, position, value):
        Argument.__init__(self, position)
        self.value = value

    def find_old_discriminator(self, discriminators):
        position = self.position
        value = self.value
        for d in discriminators:
            if isinstance(d, ValueDiscriminator) \
                    and d.position == position \
                    and api.equal_b(d.value, value):
                return d

        return None

    def make_discriminator(self):
        return ValueDiscriminator(self.position, self.value)

    def _equal_(self, other):
        if other.__class__ is self.__class__ \
                and api.equal_b(other.value, self.value) \
                and other.position == self.position:
            return True
        return False

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    def _hash_(self):
        return api.hash_i(self.value)


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


class UniqueSignature(W_Root):
    def __init__(self, args, types, method):
        self.method = method
        self.args = args
        self.types = types
        self.arity = len(args)

    def consists_of(self, types):
        if len(types) != len(self.types):
            return False

        for i in range(0, len(self.types)):
            arg1 = self.types[i]
            arg2 = types[i]

            if not api.equal_b(arg1, arg2):
                return False

        return True

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

    def has_type(self, _type):
        return api.contains_b(self.types, _type)

    def can_dispatch_on_type(self, _type, interfaces, position, strictmode=False):
        current = api.at_index(self.types, position)
        if space.isinterface(current):
            if strictmode:
                return False
            return api.contains_b(interfaces, current)
        return api.equal_b(_type, current)

    def _to_string_(self):
        return "<unique signature %s> " % (", ".join([str(arg) for arg in self.args]))


DEFAULT_RANK = 1
GUARD_RANK = 2
LITERAL_RANK = 10
WILDCARD_RANK = -5
RANKS = {
    nt.NT_INT: LITERAL_RANK,
    nt.NT_FLOAT: LITERAL_RANK,
    nt.NT_STR: LITERAL_RANK,
    nt.NT_CHAR: LITERAL_RANK,
    nt.NT_MULTI_STR: LITERAL_RANK,
    nt.NT_TRUE: LITERAL_RANK,
    nt.NT_FALSE: LITERAL_RANK,
    nt.NT_LIST: LITERAL_RANK,
    nt.NT_MAP: LITERAL_RANK,
    nt.NT_TUPLE: LITERAL_RANK,
    nt.NT_UNIT: LITERAL_RANK,
}


class Signature(UniqueSignature):
    def __init__(self, args, types, method, pattern, outers):
        UniqueSignature.__init__(self, args, types, method)
        self.pattern = pattern
        self.outers = outers

    def _to_string_(self):
        return "<signature %s> " % (", ".join([str(arg) for arg in self.args]))

    def get_weight(self):
        weight = 0
        pattern = self.pattern
        if nodes.is_guarded_pattern(self.pattern):
            weight += GUARD_RANK
            pattern = nodes.node_first(self.pattern)

        args = nodes.tuple_node_to_list(pattern)
        for arg in args:
            ntype = nodes.node_type(arg)
            weight = RANKS.get(ntype, DEFAULT_RANK)

        return weight


def _get_value_predicate(process, value, index):
    return ArgumentValue(index, value)


def _get_interface_predicate(process, interface, index):
    interfaces = process.std.interfaces

    if interfaces.Any is interface:
        arg = ArgumentAny(index)
    else:
        arg = ArgumentInterface(index, interface)

    return arg


def _get_type_predicate(process, _type, index):
    arg = ArgumentType(index, _type)
    # types = process.std.types
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


def _get_sigargs(process, args):
    arity = api.length_i(args)
    sig_args = []
    for index in range(arity):
        kind = api.at_index(args, index)
        if space.isinterface(kind):
            arg = _get_interface_predicate(process, kind, index)
        elif space.isdatatype(kind):
            arg = _get_type_predicate(process, kind, index)
        elif space.istuple(kind) and api.length_i(kind) == 2:

            argtype = api.at_index(kind, 0)
            if not api.equal_b(argtype, space.newsymbol_s(process, lang_names.SVALUEOF)):
                return error.throw_2(error.Errors.TYPE_ERROR,
                                     space.newstring(u"Invalid signature type. Expected (#VALUEOF, value)"), kind)

            value = api.at_index(kind, 1)
            arg = _get_value_predicate(process, value, index)
        else:
            return error.throw_2(error.Errors.TYPE_ERROR,
                                 space.newstring(u"Invalid signature type. Expected type or interface"), kind)

        sig_args.append(arg)
    return sig_args


def newuniquesignature(process, sig, method):
    return UniqueSignature(sig.args, sig.types, method)


def newsignature(process, args, method, pattern, outers):
    sig_args = _get_sigargs(process, args)
    return Signature(sig_args, args, method, pattern, outers)
