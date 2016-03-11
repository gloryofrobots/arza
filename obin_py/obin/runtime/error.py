from obin.types import space


def convert_to_script_error(process, err):
    return error(process, err.name, err.args_tuple)


def error(process, symbol_unistr, args_tuple):
    from obin.types import api
    assert space.istuple(args_tuple)
    assert isinstance(symbol_unistr, unicode)
    module = process.modules.get_module("err")
    symbol = space.newsymbol(process, symbol_unistr)
    err_type = api.lookup(module, symbol, space.newvoid())
    if space.isvoid(err_type):
        return space.newtuple([symbol, args_tuple])
    else:
        affirm_type(err_type, space.isdatatype)
        m = space.newpmap([space.newsymbol(process, u"args"), args_tuple])
        instance = err_type.create_instance(m)
        return instance


def signal(err):
    assert space.isany(err)
    raise ObinSignal(err)


def throw(symbol_unistr, args_tuple):
    raise ObinError(symbol_unistr, args_tuple)


def throw_0(symbol_unistr):
    throw(symbol_unistr, space.newunit())


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


def affirm_iterable(it, condition):
    for i in it:
        affirm_type(i, condition)


def affirm_type(obj, condition):
    assert space.isany(obj), obj
    if not condition(obj):
        return throw_2(Errors.TYPE_ERROR, obj, space.newstring(u"Wrong object type"))
    return True


def affirm_any(obj):
    affirm_type(obj, space.isany)


def affirm(condition, message):
    if not condition:
        return throw_1(Errors.RUNTIME_ERROR, space.newstring(message))
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


def panic(msg):
    raise RuntimeError(msg)


class Errors:
    IMPORT_ERROR = u"ImportError"
    RUNTIME_ERROR = u"RuntimeError"
    TYPE_ERROR = u"TypeError"
    REFERENCE_ERROR = u"ReferenceError"
    CONSTRUCTOR_ERROR = u"ConstructorError"
    KEY_ERROR = u"KeyError"
    VALUE_ERROR = u"ValueError"
    SLICE_ERROR = u"SliceError"
    INDEX_ERROR = u"IndexError"
    INVOKE_ERROR = u"InvokeError"
    INVALID_ARG_COUNT_ERROR = u"InvalidArgCount"
    METHOD_INVOKE_ERROR = u"MethodInvokeError"
    METHOD_NOT_IMPLEMENTED_ERROR = u"MethodNotImplementedError"
    METHOD_SPECIALIZE_ERROR = u"MethodSpecializeError"
    COMPILE_ERROR = u"CompileError"
    PARSE_ERROR = u"ParseError"
    ZERO_DIVISION_ERROR = u"ZeroDivisionError"
    UNPACK_SEQUENCE_ERROR = u"UnpackSequenceError"
    FIBER_FLOW_ERROR = u"FiberFlowError"
    NOT_IMPLEMENTED_ERROR = u"NotImplementedError"
    MATCH_ERROR = u"MatchError"
    FUNCTION_MATCH_ERROR = u"FunctionArgumentsMatchError"
    EXCEPTION_MATCH_ERROR = u"ExceptionMatchError"
    EXPORT_ERROR = u"ExportError"
    TRAIT_ALREADY_IMPLEMENTED_ERROR = u"TraitAlreadyImplementedError"
    TRAIT_IMPLEMENTATION_ERROR = u"TraitImplementationError"
    TRAIT_CONSTRAINT_ERROR = u"TraitConstraintError"


def initialise(process):
    from obin.types import api
    err_module = process.modules.get_module("err")
    for key, errname in Errors.__dict__.items():
        if not key.endswith(u"_ERROR"):
            continue

        sym = space.newsymbol(process, errname)
        if not api.contains(err_module, sym):
            panic(u"Missing type %s in prelude for internal error" % errname)
