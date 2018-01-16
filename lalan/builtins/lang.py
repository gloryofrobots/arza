from lalan.runtime.routine.routine import complete_native_routine
from lalan.runtime import error
from lalan.types import api, space, plist, environment, datatype, tuples, partial
from lalan.misc.timer import Timer

from lalan.misc.strutil import encode_unicode_utf8
from lalan.misc.platform import rstring, compute_unique_id
from lalan.misc import fs
from lalan.compile import compiler

from lalan.builtins import lang_names


def put_lang_func(process, module, name, func, arity):
    name_without_prefix = name.replace(lang_names.PREFIX, "")
    api.put_native_function(process, module, unicode(name), func, arity)
    api.put_native_function(process, module, unicode(name_without_prefix), func, arity)


def setup(process, module, stdlib):
    api.put_native_function(process, module, u'eval', __eval, 1)
    api.put_native_function(process, module, u'breakpoint', __breakpoint, -1)
    api.put_native_function(process, module, u'pl', __print, -1)
    api.put_native_function(process, module, u'address', __id, 1)
    api.put_native_function(process, module, u'time', __time, 0)
    api.put_native_function(process, module, u'get_type', __type, 1)
    put_lang_func(process, module, lang_names.APPLY, __apply, 2)
    put_lang_func(process, module, lang_names.DELAY, __delay, 1)
    put_lang_func(process, module, lang_names.NOT, __not, 1)
    put_lang_func(process, module, lang_names.IS_INDEXED, __is_indexed, 1)
    put_lang_func(process, module, lang_names.IS_SEQ, __is_seq, 1)
    put_lang_func(process, module, lang_names.IS_DICT, __is_dict, 1)
    put_lang_func(process, module, lang_names.IS, __is, 2)
    put_lang_func(process, module, lang_names.ISNOT, __isnot, 2)
    put_lang_func(process, module, lang_names.KINDOF, __kindof, 2)
    put_lang_func(process, module, lang_names.TYPE, __type, 2)
    put_lang_func(process, module, lang_names.GENERIC, __generic, 2)
    put_lang_func(process, module, lang_names.INTERFACE, __interface, 3)
    put_lang_func(process, module, lang_names.TRAIT, __trait, 3)
    put_lang_func(process, module, lang_names.EXTEND, __extend, 3)
    put_lang_func(process, module, lang_names.PARTIAL, __defpartial, 1)
    put_lang_func(process, module, u"partial", __partial, -1)

    put_lang_func(process, module, u"vector", __vector, -1)


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
def __id(process, routine):
    this = routine.get_arg(0)
    return space.newstring(unicode(hex(compute_unique_id(this))))


@complete_native_routine
def __print(process, routine):
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


# here i usually put breakpoints in python debugger
@complete_native_routine
def __breakpoint(process, routine):
    args = routine._args.to_l()
    bp = args[0]
    api.d.add_bp(api.to_i(bp))
    return space.newunit()


@complete_native_routine
def __vector(process, routine):
    args = routine._args.to_l()
    return space.newpvector(args)


def __eval(process, routine):
    x = routine.get_arg(0)

    assert space.issymbol(x)
    parent_env = routine.env
    src = api.to_s(x)
    source = compiler.compile_function_source(process, parent_env, src, space.newsymbol(process, u"__eval__"))
    env = space.newenv(space.newsymbol(process, u"__eval__"), source.code.scope, parent_env)

    func = space.newfunc(source.name, source.code, env)
    args = space.newunit()
    api.call(process, func, args)


def __apply(process, routine):
    func = routine.get_arg(0)
    args = routine.get_arg(1)
    if space.islist(args):
        args = plist.to_tuple(args)
    elif not space.istuple(args):
        # args = space.newtuple([args])
        return error.throw_1(error.Errors.TYPE_ERROR, space.newstring(u"expected tuple"))
    api.call(process, func, args)


@complete_native_routine
def __type(process, routine):
    left = routine.get_arg(0)
    return api.get_type(process, left)


@complete_native_routine
def __delay(process, routine):
    left = routine.get_arg(0)
    error.affirm_type(left, space.isfunction)
    return space.newlazyval(left)


@complete_native_routine
def __not(process, routine):
    left = routine.get_arg(0)
    error.affirm_type(left, space.isboolean)
    return api.not_(left)


@complete_native_routine
def __type(process, routine):
    name = routine.get_arg(0)
    fields = routine.get_arg(1)
    _datatype = space.newdatatype(process, name, fields)
    return _datatype


@complete_native_routine
def __generic(process, routine):
    name = routine.get_arg(0)
    signature = routine.get_arg(1)
    method = space.newgeneric(name, signature)
    return method


@complete_native_routine
def __interface(process, routine):
    name = routine.get_arg(0)
    generics = routine.get_arg(1)
    mixins = routine.get_arg(2)
    interface = space.newinterface_extended(name, generics, mixins)
    return interface


@complete_native_routine
def __trait(process, routine):
    name = routine.get_arg(0)
    constraints = routine.get_arg(1)
    generics = routine.get_arg(2)
    if space.istuple(constraints):
        constraints = tuples.to_list(constraints)
    _trait = space.newtrait(name, constraints, generics)
    return _trait


@complete_native_routine
def __extend(process, routine):
    _type = routine.get_arg(0)
    _mixins = routine.get_arg(1)
    _methods = routine.get_arg(2)
    _type = datatype.extend(_type, _mixins, _methods)

    return _type


@complete_native_routine
def __defpartial(process, routine):
    func = routine.get_arg(0)
    return space.newpartial(func)


@complete_native_routine
def __partial(process, routine):
    args = routine._args.to_l()
    func = args[0]
    args_t = space.newtuple(args[1:])
    return partial.newfunction_partial(func, args_t)


@complete_native_routine
def __time(process, routine):
    import time
    return space.newfloat(time.time())


@complete_native_routine
def __is_indexed(process, routine):
    v1 = routine.get_arg(0)
    if space.istuple(v1) or space.isarguments(v1):
        return space.newbool(True)

    if api.kindof_b(process, v1, process.std.interfaces.Indexed):
        return space.newbool(True)

    return space.newbool(False)


@complete_native_routine
def __is_seq(process, routine):
    from lalan.types.space import islist, newbool
    v1 = routine.get_arg(0)
    if islist(v1):
        return newbool(True)
    if api.kindof_b(process, v1, process.std.interfaces.Seq):
        return newbool(True)

    return newbool(False)


@complete_native_routine
def __is_dict(process, routine):
    v1 = routine.get_arg(0)

    if space.ispmap(v1):
        return space.newbool(True)

    if api.kindof_b(process, v1, process.std.interfaces.Dict):
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
