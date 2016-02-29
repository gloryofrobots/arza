from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error
from obin.types import api, space, plist, environment, entity

from obin.runistr import encode_unicode_utf8
from obin.misc.platform import rstring, compute_unique_id
from obin.misc import fs
from obin.compile import compiler

PRIM_IS_INDEXED = "___is_indexed"
PRIM_IS_SEQ = "___is_seq"
PRIM_IS_MAP = "___is_map"
PRIM_LENGTH = "___length"
PRIM_FIRST = "___first"
PRIM_REST = "___rest"
PRIM_IS = "___is"
PRIM_ISNOT = "___isnot"
PRIM_NOTA = "___nota"
PRIM_ISA = "___isa"
PRIM_KINDOF = "___kindof"

def setup(process, module, stdlib):
    api.put_native_function(process, module, u'eval', _eval, 1)
    api.put_native_function(process, module, u'print', _print, -1)
    api.put_native_function(process, module, u'id', _id, 1)
    api.put_native_function(process, module, u'apply', apply, 2)
    api.put_native_function(process, module, u'concat', concat_tuples, 2)
    api.put_native_function(process, module, u'time', time, 0)
    api.put_native_function(process, module, u'traits', traits, 1)
    api.put_native_function(process, module, u'range', _range, 2)
    api.put_native_function(process, module, unicode(PRIM_IS_INDEXED), is_indexed, 1)
    api.put_native_function(process, module, unicode(PRIM_IS_SEQ), is_seq, 1)
    api.put_native_function(process, module, unicode(PRIM_IS_MAP), is_map, 1)
    api.put_native_function(process, module, unicode(PRIM_LENGTH), length, 1)
    api.put_native_function(process, module, unicode(PRIM_IS), __is, 2)
    api.put_native_function(process, module, unicode(PRIM_ISNOT), __isnot, 2)
    api.put_native_function(process, module, unicode(PRIM_NOTA), __nota, 2)
    api.put_native_function(process, module, unicode(PRIM_ISA), __isa, 2)
    api.put_native_function(process, module, unicode(PRIM_KINDOF), __kindof, 2)


    ## debugging
    # if not we_are_translated():
    #     api.put_native_function(process, obj, u'pypy_repr', pypy_repr)
    #     api.put_native_function(process, obj, u'inspect', inspect)


# 15.1.2.2

@complete_native_routine
def compile_module(process, routine):
    sourcename = routine.get_arg(0)
    modulename = routine.get_arg(1)
    parent_env = routine.get_arg(2)
    filename = api.to_s(sourcename)
    script = fs.load_file_content(filename)

    _module = compiler.compile_env(process, parent_env, modulename, script, sourcename)
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
        return space.newnil()

    builder = rstring.UnicodeBuilder()
    for arg in args[:-1]:
        builder.append(api.to_u(arg))
        builder.append(u' ')

    builder.append(api.to_u(args[-1]))

    u_print_str = builder.build()
    print_str = encode_unicode_utf8(u_print_str)
    print print_str
    return space.newnil()


def _eval(process, routine):
    x = routine.get_arg(0)

    assert space.issymbol(x)
    parent_env = routine.env
    src = api.to_s(x)
    source = compiler.compile_function_source(process, parent_env, src, space.newsymbol(process, u"__eval__"))
    env = space.newenv(space.newsymbol(process, u"__eval__"), source.code.scope, parent_env)

    func = space.newfunc(source.name, source.code, env)
    args = space.newtuple([])
    api.call(process, func, args)


def apply(process, routine):
    func = routine.get_arg(0)
    args = routine.get_arg(1)
    if space.islist(args):
        args = plist.to_tuple(args)
    elif not space.istuple(args):
        return error.throw_1(error.Errors.TYPE, space.newstring(u"arguments tuple expected"))
    api.call(process, func, args)


@complete_native_routine
def concat_tuples(process, routine):
    from obin.types.tupl import concat
    v1 = routine.get_arg(0)
    v2 = routine.get_arg(1)
    return concat(process, v1, v2)


@complete_native_routine
def time(process, routine):
    import time
    return space.newfloat(time.time())


@complete_native_routine
def is_indexed(process, routine):
    v1 = routine.get_arg(0)
    if not space.isvector(v1) and not space.istuple(v1):
        return space.newbool(False)
    return space.newbool(True)


@complete_native_routine
def is_seq(process, routine):
    from obin.types.space import islist, newbool
    v1 = routine.get_arg(0)
    if not islist(v1):
        return newbool(False)
    return newbool(True)


@complete_native_routine
def is_map(process, routine):
    v1 = routine.get_arg(0)
    if not space.ispmap(v1):
        return space.newbool(False)
    return space.newbool(True)


@complete_native_routine
def length(process, routine):
    v1 = routine.get_arg(0)
    return api.length(v1)


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
    return entity.kindof(process, left, right)

@complete_native_routine
def __nota(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return entity.nota(process, left, right)

@complete_native_routine
def __isa(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
    return entity.isa(process, left, right)


@complete_native_routine
def _range(process, routine):
    start = routine.get_arg(0)
    end = routine.get_arg(1)
    start = api.to_i(start)
    end = api.to_i(end)
    items = [space.newint(i) for i in xrange(start, end)]
    return space.newtuple(items)


@complete_native_routine
def clone(process, routine):
    origin = routine.get_arg(0)
    clone = api.clone(origin)
    return clone


@complete_native_routine
def traits(process, routine):
    obj = routine.get_arg(0)
    return api.traits(process, obj)


@complete_native_routine
def lookup(process, routine):
    this = routine.get_arg(0)
    key = routine.get_arg(1)
    default = routine.get_arg(2)
    return api.lookup(this, key, default)


@complete_native_routine
def clone(process, routine):
    this = routine.get_arg(0)
    return api.clone(this)


@complete_native_routine
def trait(process, routine):
    name = routine.get_arg(0)
    return space.newtrait(name)
