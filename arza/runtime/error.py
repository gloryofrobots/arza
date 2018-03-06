from arza.types import space


def convert_to_script_error(process, err):
    return error(process, err.name, err.args_tuple)


def error(process, symbol_unistr, args_tuple):
    from arza.types import environment, api
    assert space.istuple(args_tuple)
    assert isinstance(symbol_unistr, unicode)
    module = process.modules.prelude
    symbol = space.newsymbol(process, symbol_unistr)
    err_type = environment.get_value(module, symbol)
    if space.isvoid(err_type):
        return space.newtuple([symbol, args_tuple])
    else:
        affirm_type(err_type, space.isdatatype)
        instance = api.call(process, err_type, space.newtuple([args_tuple]))
        return instance


def signal(err):
    assert space.isany(err)
    raise ArzaSignal(err)


def throw(symbol_unistr, args_tuple):
    raise ArzaError(symbol_unistr, args_tuple)


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


def throw_6(symbol_unistr, arg1, arg2, arg3, arg4, arg5, arg6):
    throw(symbol_unistr, space.newtuple([arg1, arg2, arg3, arg4, arg5, arg6]))


def throw_7(symbol_unistr, arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    throw(symbol_unistr, space.newtuple([arg1, arg2, arg3, arg4, arg5, arg6, arg7]))


def affirm_iterable(it, condition):
    for i in it:
        affirm_type(i, condition)


def affirm_type(obj, condition, expected=None):
    if not condition(obj):
        if expected:
            expected_str= u"expected %s" % expected
        else:
            expected_str = u""
        return throw_2(Errors.TYPE_ERROR, space.safe_w(obj),
                       space.newstring(u"Wrong object type %s" % expected_str))
    return True


def affirm_any(obj):
    affirm_type(obj, space.isany)


def affirm(condition, message):
    if not condition:
        return throw_1(Errors.RUNTIME_ERROR, space.newstring(message))
    return True


class ArzaError(Exception):
    def __init__(self, name, args_tuple):
        self.name = name
        self.args_tuple = args_tuple

    def __str__(self):
        from arza.types import api
        return "%s%s" % (str(self.name), api.to_s(self.args_tuple))

    def __repr__(self):
        return self.__str__()


class ArzaSignal(Exception):
    def __init__(self, signal):
        self.signal = signal

    def __str__(self):
        from arza.types import api
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
    OVERFLOW_ERROR = u"OverflowError"
    MATH_DOMAIN_ERROR = u"MathDomainError"
    UNPACK_SEQUENCE_ERROR = u"UnpackSequenceError"
    FIBER_FLOW_ERROR = u"FiberFlowError"
    NOT_IMPLEMENTED_ERROR = u"NotImplementedError"
    MATCH_ERROR = u"MatchError"
    FUNCTION_MATCH_ERROR = u"FunctionArgumentsMatchError"
    EXCEPTION_MATCH_ERROR = u"ExceptionMatchError"
    EXPORT_ERROR = u"ExportError"
    IMPLEMENTATION_ERROR = u"ImplementationError"
    CONSTRAINT_ERROR = u"ConstraintError"


def initialise(process):
    from arza.types import api
    err_module = process.modules.prelude
    for key, errname in Errors.__dict__.items():
        if not key.endswith(u"_ERROR"):
            continue

        sym = space.newsymbol(process, errname)
        err_type = api.lookup(err_module, sym, space.newvoid())
        if space.isvoid(err_type):
            panic(u"Missing type %s in prelude for internal error" % errname)
