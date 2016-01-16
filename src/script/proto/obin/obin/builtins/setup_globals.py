# -*- coding: utf-8 -*-
from obin.runtime.routine import complete_native_routine
from obin.types import api
from obin.types import space
from rpython.rlib.rstring import UnicodeBuilder
from obin.runistr import encode_unicode_utf8


def setup(process, module, stdlib):
    ### Traits

    # 15.1.2.1
    api.put_native_function(process, module, u'eval', _eval, 1)
    api.put_native_function(process, module, u'print', _print, -1)
    api.put_native_function(process, module, u'id', _id, 1)
    api.put_native_function(process, module, u'spawn_fiber', spawn_fiber, 0)
    api.put_native_function(process, module, u'activate_fiber', activate_fiber, 2)
    api.put_native_function(process, module, u'range', _range, 2)
    api.put_native_function(process, module, u'clone', clone, 1)
    api.put_native_function(process, module, u'trait', trait, 1)
    api.put_native_function(process, module, u'attach', attach, -1)
    api.put_native_function(process, module, u'detach', detach, -1)
    api.put_native_function(process, module, u'apply', apply, 2)
    api.put_native_function(process, module, u'concat', concat_tuples, 2)
    api.put_native_function(process, module, u'time', time, 0)
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
def _id(process, routine):
    from rpython.rlib.objectmodel import compute_unique_id
    this = routine.get_arg(0)
    return space.newstring(unicode(hex(compute_unique_id(this))))


@complete_native_routine
def _print(process, routine):
    args = routine._args.to_py_list()
    if len(args) == 0:
        return

    builder = UnicodeBuilder()
    for arg in args[:-1]:
        builder.append(api.to_native_unicode(arg))
        builder.append(u' ')

    builder.append(api.to_native_unicode(args[-1]))

    u_print_str = builder.build()
    print_str = encode_unicode_utf8(u_print_str)
    print(print_str)
    return space.newundefined()


def _eval(process, routine):
    from obin.runtime.environment import newenv
    from obin.compile import compiler
    x = routine.get_arg(0)

    assert space.issymbol(x)
    src = api.to_native_string(x)
    source = compiler.compile_function_source(process, src, space.newsymbol(process, u"__eval__"))
    obj = source.code.scope.create_env_bindings()
    env = newenv(obj, None)
    func = space.newfunc(source.name, source.code, env)
    args = space.newtuple([])
    api.call(process, func, args)


def apply(process, routine):
    func = routine.get_arg(0)
    args = routine.get_arg(1)
    from obin.types.space import istuple
    assert istuple(args)
    api.call(process, func, args)


@complete_native_routine
def concat_tuples(process, routine):
    from obin.types.tupl import concat
    v1 = routine.get_arg(0)
    v2 = routine.get_arg(1)
    return concat(process, v1, v2)


@complete_native_routine
def time(process, routine):
    from obin.types.space import newfloat
    import time
    return newfloat(time.time())


@complete_native_routine
def is_indexed(process, routine):
    from obin.types.space import isvector, istuple, newbool
    v1 = routine.get_arg(0)
    if not isvector(v1) and not istuple(v1):
        return newbool(False)
    return newbool(True)


@complete_native_routine
def is_seq(process, routine):
    from obin.types.space import islist, newbool
    v1 = routine.get_arg(0)
    if not islist(v1):
        return newbool(False)
    return newbool(True)


@complete_native_routine
def is_map(process, routine):
    from obin.types.space import ismap, newbool
    v1 = routine.get_arg(0)
    if not ismap(v1):
        return newbool(False)
    return newbool(True)


@complete_native_routine
def length(process, routine):
    v1 = routine.get_arg(0)
    return api.length(v1)


@complete_native_routine
def first(process, routine):
    from obin.types.plist import head, isempty
    from obin.types.space import islist
    lst = routine.get_arg(0)
    assert islist(lst)
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
    return space.newundefined()


@complete_native_routine
def _range(process, routine):
    start = routine.get_arg(0)
    end = routine.get_arg(1)
    start = api.to_native_integer(start)
    end = api.to_native_integer(end)
    items = [space.newint(i) for i in xrange(start, end)]
    return space.newtuple(items)


@complete_native_routine
def clone(process, routine):
    origin = routine.get_arg(0)
    clone = api.clone(origin)
    return clone


@complete_native_routine
def traits(process, routine):
    from obin.types import behavior
    obj = routine.get_arg(0)
    return behavior.traits(process, obj)


@complete_native_routine
def attach(process, routine):
    args = routine.args().to_py_list()
    obj = routine.get_arg(0)
    for i in range(len(args) - 1, 0, -1):
        trait = routine.get_arg(i)
        api.attach(process, obj, trait)
    return obj


@complete_native_routine
def detach(process, routine):
    args = routine.args().to_py_list()
    obj = routine.get_arg(0)
    for i in range(1, len(args)):
        trait = routine.get_arg(i)
        api.detach(process, obj, trait)

    return obj


@complete_native_routine
def kindof(process, routine):
    obj = routine.get_arg(0)
    trait = routine.get_arg(1)
    return api.kindof(trait, obj)


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
