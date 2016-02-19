from obin.types import space


def convert_to_script_error(process, err):
    return error(process, err.name, err.args_tuple)


def error(process, symbol_unistr, args_tuple):
    assert space.istuple(args_tuple)
    assert isinstance(symbol_unistr, unicode)
    symbol = space.newsymbol(process, symbol_unistr)
    return space.newtuple([symbol, args_tuple])


def signal(err):
    assert space.isany(err)
    raise ObinSignal(err)


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


def affirm_type(obj, condition):
    if not condition(obj):
        return throw_1(Errors.TYPE, obj)
    return True


def affirm_any(obj):
    affirm_type(obj, space.isany)


def affirm(condition, message):
    if not condition:
        return throw_1(Errors.RUNTIME, space.newstring(message))
    return True


class ObinError(Exception):
    def __init__(self, name, args_tuple):
        self.name = name
        self.args_tuple = args_tuple

    def __str__(self):
        from obin.types import api
        return "%s%s" % (str(self.name), api.to_s(self.args_tuple))

    def __repr__(self):
        return self.__str__()


class ObinSignal(Exception):
    def __init__(self, signal):
        self.signal = signal

    def __str__(self):
        from obin.types import api
        return api.to_s(self.signal)

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
    INVALID_ARG_COUNT = u"InvalidArgCount"
    METHOD_INVOKE = u"MethodInvokeError"
    METHOD_SPECIALIZE = u"MethodSpecializeError"
    FROZEN = u"FrozenValueIllegalOperationError"
    COMPILE = u"CompileError"
    PARSE = u"ParseError"
    ZERO_DIVISION = u"ZeroDivisionError"
    UNPACK_SEQUENCE = u"UnpackSequenceError"
    FIBER_FLOW = u"FiberFlowError"
    NOT_IMPLEMENTED = u"NotImplementedError"
    MATCH = u"MatchError"
    FUNCTION_MATCH = u"FunctionArgumentsMatchError"
    EXCEPTION_MATCH = u"ExceptionMatchError"
    EXPORT = u"ExportError"
