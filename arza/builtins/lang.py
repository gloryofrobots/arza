from arza.runtime.routine.routine import complete_native_routine
from arza.runtime import error
from arza.types import api, space, plist, environment, datatype, partial
from arza.types.dispatch import generic

from arza.misc.strutil import encode_unicode_utf8
from arza.misc.platform import rstring, compute_unique_id
from arza.misc import fs
from arza.compile import compiler

from arza.builtins import lang_names


def put_lang_func(process, module, name, func, arity):
    name_without_prefix = name.replace(lang_names.PREFIX, "")
    api.put_native_function(process, module, unicode(name), func, arity)
    api.put_native_function(process, module, unicode(name_without_prefix), func, arity)


def setup(process, module, stdlib):
    api.put_native_function(process, module, u'eval', _eval, 1)
    api.put_native_function(process, module, u'_exit', _exit, -1)
    api.put_native_function(process, module, u'__env__', __env, 0)
    api.put_native_function(process, module, u'DMARK', __dmark, -1)
    api.put_native_function(process, module, u'PL', _print, -1)
    api.put_native_function(process, module, u'address', _id, 1)
    api.put_native_function(process, module, u'time', time, 0)
    api.put_native_function(process, module, u'get_type', _type, 1)
    api.put_native_function(process, module, u'method', __method, 2)
    api.put_native_function(process, module, u'signatures', __signatures, 1)
    api.put_native_function(process, module, u'symbol', _symbol, 1)
    put_lang_func(process, module, lang_names.APPLY, apply, 2)
    put_lang_func(process, module, lang_names.NOT, __not, 1)
    put_lang_func(process, module, lang_names.IS_INDEXED, is_indexed, 1)
    put_lang_func(process, module, lang_names.IS_TUPLE, is_tuple, 1)
    put_lang_func(process, module, lang_names.IS_SEQ, is_seq, 1)
    put_lang_func(process, module, lang_names.IS_DICT, is_dict, 1)
    put_lang_func(process, module, lang_names.IS, __is, 2)
    put_lang_func(process, module, lang_names.ISNOT, __isnot, 2)
    put_lang_func(process, module, lang_names.KINDOF, __kindof, 2)
    put_lang_func(process, module, lang_names.IS_IMPLEMENTED, __is_implemented, 2)
    put_lang_func(process, module, lang_names.GENERIC, __generic, 2)
    put_lang_func(process, module, lang_names.INTERFACE, __interface, 3)
    put_lang_func(process, module, lang_names.SPECIFY, __specify, 5)
    put_lang_func(process, module, lang_names.OVERRIDE, __override, 5)
    put_lang_func(process, module, lang_names.DESCRIBE, __describe, 2)
    put_lang_func(process, module, lang_names.TYPE, __type, 3)
    put_lang_func(process, module, lang_names.CHECK_RECORD, __check_record, 2)
    put_lang_func(process, module, lang_names.LOAD_MODULE, load_module, 1)
    # put_lang_func(process, module, lang_names.CURRY, __curry, 1)
    put_lang_func(process, module, u"curry", __curry, 1)
    put_lang_func(process, module, u"partial", __partial, -1)
    put_lang_func(process, module, u"interfaces", __interfaces, 1)
    put_lang_func(process, module, u"vector", __vector, -1)
    put_lang_func(process, module, u"array", __array, -1)


# 15.1.2.2

@complete_native_routine
def compile_module(process, routine):
    sourcename = routine.get_arg(0)
    modulename = routine.get_arg(1)
    parent_env = routine.get_arg(2)
    filename = api.to_s(sourcename)
    script = fs.load_file_content(filename)

    # with Timer("--- compile module  %s " % api.to_s(modulename)):
    _module = compiler.compile_env(process, parent_env, modulename, script, sourcename)

    # print("--- compile module  %s seconds %d ---" % (, (time.time() - start_time)))
    env = environment.create_environment(process, _module, parent_env)
    return env


@complete_native_routine
def _id(process, routine):
    this = routine.get_arg(0)
    return space.newstring(unicode(hex(compute_unique_id(this))))


@complete_native_routine
def _print(process, routine):
    args = routine._args.to_l()
    if len(args) == 0:
        return space.newunit()

    builder = rstring.UnicodeBuilder()
    for arg in args[:-1]:
        builder.append(api.to_u(arg))
        builder.append(u' ')

    builder.append(api.to_u(args[-1]))

    u_print_str = builder.build()
    print_str = encode_unicode_utf8(u_print_str)
    print print_str
    return space.newunit()


@complete_native_routine
def __env(process, routine):
    from arza.runtime.routine.code_routine import CodeRoutine
    prev = process.fiber.previous_routine()
    if not isinstance(prev, CodeRoutine):
        return space.newunit()

    return prev.env


# here i can put breakpoints in python debugger
# and pause script execution
@complete_native_routine
def __dmark(process, routine):
    _num = routine.get_arg(0)
    error.affirm_type(_num, space.isint)
    api.d.add_bp(api.to_i(_num))
    return space.newunit()


@complete_native_routine
def __vector(process, routine):
    args = routine._args.to_l()
    return space.newpvector(args)


@complete_native_routine
def __array(process, routine):
    args = routine._args.to_l()
    return space.newarray(args)


def _exit(process, routine):
    print routine._args.to_l()
    raise SystemExit


def _eval(process, routine):
    x = routine.get_arg(0)

    assert space.issymbol(x)
    parent_env = routine.env
    src = api.to_s(x)
    source = compiler.compile_function_source(process, parent_env, src, space.newsymbol(process, u"__eval__"))
    env = space.newenv(space.newsymbol(process, u"__eval__"), source.code.scope, parent_env)

    func = space.newfunc(source.name, source.code, env)
    args = space.newunit()
    api.call(process, func, args)


def apply(process, routine):
    func = routine.get_arg(0)
    args = routine.get_arg(1)
    if space.islist(args):
        args = plist.to_tuple(args)
    elif not space.istuple(args):
        # args = space.newtuple([args])
        return error.throw_1(error.Errors.TYPE_ERROR, space.newstring(u"expected tuple"))
    api.call(process, func, args)


@complete_native_routine
def _type(process, routine):
    left = routine.get_arg(0)
    return api.get_type(process, left)


@complete_native_routine
def _symbol(process, routine):
    _str = routine.get_arg(0)
    error.affirm_type(_str, space.isstring)
    return space.newsymbol_string(process, _str)


@complete_native_routine
def __not(process, routine):
    left = routine.get_arg(0)
    error.affirm_type(left, space.isboolean)
    return api.not_(left)


@complete_native_routine
def __type(process, routine):
    name = routine.get_arg(0)
    fields = routine.get_arg(1)
    construct = routine.get_arg(2)
    _datatype = space.newdatatype(process, name, fields, construct)
    return _datatype


@complete_native_routine
def __generic(process, routine):
    name = routine.get_arg(0)
    sig = routine.get_arg(1)
    return generic.generic(process, name, sig)


@complete_native_routine
def __override(process, routine):
    gf = routine.get_arg(0)
    types = routine.get_arg(1)
    method = routine.get_arg(2)
    pattern = routine.get_arg(3)
    outers = routine.get_arg(4)
    generic.override(process, gf, types, method, pattern, outers)
    return gf


@complete_native_routine
def __specify(process, routine):
    gf = routine.get_arg(0)
    types = routine.get_arg(1)
    method = routine.get_arg(2)
    pattern = routine.get_arg(3)
    outers = routine.get_arg(4)
    generic.specify(process, gf, types, method, pattern, outers)
    return gf


@complete_native_routine
def __interface(process, routine):
    name = routine.get_arg(0)
    generics = routine.get_arg(1)
    sub_interfaces = routine.get_arg(2)
    interface = space.newinterface(name, generics, sub_interfaces)
    return interface


@complete_native_routine
def __method(process, routine):
    fn = routine.get_arg(0)
    types = routine.get_arg(1)
    error.affirm_type(fn, space.isgeneric)
    error.affirm_type(types, space.islist)
    error.affirm_iterable(types, space.isspecializable)
    return generic.get_method(process, fn, types)


@complete_native_routine
def __signatures(process, routine):
    fn = routine.get_arg(0)
    error.affirm_type(fn, space.isgeneric)
    return generic.signatures(process, fn)


@complete_native_routine
def __describe(process, routine):
    _type = routine.get_arg(0)
    interfaces = routine.get_arg(1)
    datatype.derive_strict(process, _type, interfaces)
    return _type


@complete_native_routine
def __check_record(process, routine):
    _type = routine.get_arg(0)
    record = routine.get_arg(1)
    _type.validate(process, record)
    return record




@complete_native_routine
def load_module(process, routine):
    from arza.runtime import load
    module_path = routine.get_arg(0)
    if space.isstring(module_path):
        module_path = space.newsymbol_string(process, module_path)

    error.affirm_type(module_path, space.issymbol)
    module = load.import_module(process, module_path)
    return module


@complete_native_routine
def __curry(process, routine):
    func = routine.get_arg(0)
    return space.newpartial(func)


@complete_native_routine
def __partial(process, routine):
    args = routine._args.to_l()
    func = args[0]
    args_t = space.newtuple(args[1:])
    return partial.newfunction_partial(func, args_t)


@complete_native_routine
def time(process, routine):
    import time
    return space.newfloat(time.time())


@complete_native_routine
def is_tuple(process, routine):
    v1 = routine.get_arg(0)
    if space.istuple(v1) or space.isarguments(v1):
        return space.newbool(True)

    return space.newbool(False)


@complete_native_routine
def is_indexed(process, routine):
    v1 = routine.get_arg(0)
    if space.istuple(v1) or space.isarguments(v1):
        return space.newbool(True)

    if api.kindof_b(process, v1, process.std.interfaces.Indexed):
        return space.newbool(True)

    return space.newbool(False)


@complete_native_routine
def is_seq(process, routine):
    from arza.types.space import islist, newbool
    v1 = routine.get_arg(0)
    if islist(v1):
        return newbool(True)
    if api.kindof_b(process, v1, process.std.interfaces.Seq):
        return newbool(True)

    return newbool(False)


@complete_native_routine
def is_dict(process, routine):
    v1 = routine.get_arg(0)

    if space.ispmap(v1):
        return space.newbool(True)

    if api.kindof_b(process, v1, process.std.interfaces.Dict):
        return space.newbool(True)

    if api.kindof_b(process, v1, process.std.interfaces.Instance):
        return space.newbool(True)

    return space.newbool(False)


@complete_native_routine
def __is(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return api.is_(left, right)


@complete_native_routine
def __isnot(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return api.isnot(left, right)


@complete_native_routine
def __kindof(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return api.kindof(process, left, right)


@complete_native_routine
def __is_implemented(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return api.is_implemented(process, left, right)


@complete_native_routine
def __interfaces(process, routine):
    obj = routine.get_arg(0)
    if space.isdatatype(obj):
        return datatype.get_interfaces(process, obj)
    else:
        return datatype.get_interfaces(process, api.get_type(process, obj))
