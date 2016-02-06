# -*- coding: utf-8 -*-
from obin.runtime.routine import complete_native_routine
from obin.runtime import error
from obin.types import api, space, plist, module
from rpython.rlib.rstring import UnicodeBuilder
from obin.runistr import encode_unicode_utf8
from rpython.rlib.objectmodel import compute_unique_id
from obin.utils import fs
from obin.compile import compiler

def setup(process, module, stdlib):
    ### Traits

    # 15.1.2.1
    api.put_native_function(process, module, u'eval', _eval, 1)
    api.put_native_function(process, module, u'print', _print, -1)
    api.put_native_function(process, module, u'id', _id, 1)
    api.put_native_function(process, module, u'spawn_fiber', spawn_fiber, 0)
    api.put_native_function(process, module, u'activate_fiber', activate_fiber, 2)
    api.put_native_function(process, module, u'range', _range, 2)
    api.put_native_function(process, module, u'apply', apply, 2)
    api.put_native_function(process, module, u'concat', concat_tuples, 2)
    api.put_native_function(process, module, u'time', time, 0)
    api.put_native_function(process, module, u'traits', traits, 1)
    api.put_native_function(process, module, u'is_indexed', is_indexed, 1)
    api.put_native_function(process, module, u'is_seq', is_seq, 1)
    api.put_native_function(process, module, u'is_map', is_map, 1)

    api.put_native_function(process, module, u'length', length, 1)
    api.put_native_function(process, module, u'first', first, 1)
    api.put_native_function(process, module, u'rest', rest, 1)
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

    _module = compiler.compile_module(process, modulename, script, sourcename)
    module.create_environment(process, _module, parent_env)
    return _module

@complete_native_routine
def _id(process, routine):
    this = routine.get_arg(0)
    return space.newstring(unicode(hex(compute_unique_id(this))))


@complete_native_routine
def _print(process, routine):
    args = routine._args.to_l()
    if len(args) == 0:
        return space.newnil()

    builder = UnicodeBuilder()
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
    src = api.to_s(x)
    source = compiler.compile_function_source(process, src, space.newsymbol(process, u"__eval__"))
    obj = source.code.scope.create_env_bindings()
    env = space.newenv(obj, None)
    func = space.newfunc(source.name, source.code, env)
    args = space.newtuple([])
    api.call(process, func, args)


def apply(process, routine):
    func = routine.get_arg(0)
    args = routine.get_arg(1)
    if not space.istuple(args):
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
def first(process, routine):
    from obin.types.plist import head
    lst = routine.get_arg(0)
    assert space.islist(lst)
    v = head(lst)
    return v


@complete_native_routine
def rest(process, routine):
    from obin.types.plist import tail, isempty
    from obin.types.space import islist
    lst = routine.get_arg(0)
    assert islist(lst)
    assert not isempty(lst)
    v = tail(lst)
    return v


@complete_native_routine
def spawn_fiber(process, routine):
    from obin.types.fiber import newfiber
    y1, y2 = newfiber(process)
    return space.newtuple([y1, y2])


def activate_fiber(process, routine):
    from obin.types.fiber import activate_fiber as activate
    fiber = routine.get_arg(0)
    func = routine.get_arg(1)
    # args = routine.get_arg(2)
    args = space.newtuple([])
    activate(process, fiber, func, args)
    return space.newnil()


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
