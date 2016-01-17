from obin.types import api, space


def error(process, symbol_unistr, args_tuple):
    assert space.istuple(args_tuple)
    assert isinstance(symbol_unistr, unicode)
    symbol = space.newsymbol(process, symbol_unistr)
    return space.newtuple([symbol, args_tuple])


def throw(symbol_unistr, args_tuple):
    raise ObinError(symbol_unistr, args_tuple)

def throw_0(symbol_unistr):
    throw(symbol_unistr, space.newtuple([]))

def throw_1(symbol_unistr, arg):
    throw(symbol_unistr, space.newtuple([arg]))


def throw_2(symbol_unistr, arg1, arg2):
    throw(symbol_unistr, space.newtuple([arg1, arg2]))


def throw_3(symbol_unistr, arg1, arg2, arg3):
    throw(symbol_unistr, space.newtuple([arg1, arg2, arg3]))


def throw_4(symbol_unistr, arg1, arg2, arg3, arg4):
    throw(symbol_unistr, space.newtuple([arg1, arg2, arg3, arg4]))


def throw_5(symbol_unistr, arg1, arg2, arg3, arg4, arg5):
    throw(symbol_unistr, space.newtuple([arg1, arg2, arg3, arg4, arg5]))


class ObinError(Exception):
    def __init__(self, name, args_tuple):
        self.name = name
        self.args_tuple = args_tuple

    def __str__(self):
        return "%s%s" % (str(self.name), api.to_native_string(self.args_tuple))

    def __repr__(self):
        return self.__str__()


class Errors:
    IMPORT = u"ImportError"
    RUNTIME = u"RuntimeError"
    ADD_TRAIT = u"AddTraitError"
    REMOVE_TRAIT = u"RemoveTraitError"
    TYPE = u"TypeError"
    REFERENCE = u"ReferenceError"
    RANGE = u"RangeError"
    KEY = u"KeyError"
    VALUE = u"ValueError"
    SLICE = u"SliceError"
    INDEX = u"IndexError"
    INVOKE = u"InvokeError"
    METHOD_INVOKE = u"MethodInvokeError"
    METHOD_SPECIALIZE = u"MethodSpecializeError"
    FROZEN = u"FrozenValueIllegalOperationError"
    COMPILE = u"CompileError"
    PARSE = u"Parse"
    ZERO_DIVISION = u"ZeroDivisionError"
    UNPACK_SEQUENCE = u"UnpackSequenceError"
    ORIGINATE = u"OriginateError"
    FIBER_FLOW = u"FiberFlowError"
    NOT_IMPLEMENTED = u"NotImplementedError"


class ObinMethodInvokeError(ObinRangeError):
    def __init__(self, method, args):
        self.arguments = args
        self.method = method

    def _msg(self):
        return u'Method Invoke Error:  Can\'t determine method "%s" for arguments %s' % (
            str(self.method._name_), str(self.arguments),)


class ObinMethodSpecialisationError(ObinRangeError):
    def __init__(self, method, message):
        self.method = method
        self.message = message

    def _msg(self):
        return u'Method Specialisation Error:  Can\'t specialize method "%s" %s' % (
            str(self.method._name_), str(self.message),)
