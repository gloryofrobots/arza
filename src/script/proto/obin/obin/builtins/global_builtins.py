# -*- coding: utf-8 -*-
from obin.runtime.routine import complete_native_routine
from obin.objects import api
from rpython.rlib.rstring import UnicodeBuilder
from obin.runistr import encode_unicode_utf8


def setup(obj):
    from rpython.rlib.objectmodel import we_are_translated
    from obin.objects.space import state

    ### Traits
    traits = state.traits
    api.put_property(obj, u'Any', traits.Any)
    api.put_property(obj, u'True', traits.True)
    api.put_property(obj, u'False', traits.False)
    api.put_property(obj, u'Boolean', traits.Boolean)
    api.put_property(obj, u'Nil', traits.Nil)
    api.put_property(obj, u'Undefined', traits.Undefined)
    api.put_property(obj, u'Char', traits.Char)
    api.put_property(obj, u'Number', traits.Number)
    api.put_property(obj, u'Integer', traits.Integer)
    api.put_property(obj, u'Float', traits.Float)
    api.put_property(obj, u'Symbol', traits.Symbol)
    api.put_property(obj, u'String', traits.String)
    api.put_property(obj, u'Vector', traits.Vector)
    api.put_property(obj, u'Tuple', traits.Tuple)
    api.put_property(obj, u'Object', traits.Object)
    api.put_property(obj, u'Generic', traits.Generic)
    api.put_property(obj, u'Module', traits.Module)
    api.put_property(obj, u'Primitive', traits.Primitive)
    api.put_property(obj, u'Function', traits.Function)

    # 15.1.2.1
    api.put_native_function(obj, u'eval', _eval, 1)
    api.put_native_function(obj, u'print', _print, -1)
    api.put_native_function(obj, u'id', _id, 1)
    api.put_native_function(obj, u'coroutine', coroutine, 1)
    api.put_native_function(obj, u'range', _range, 2)
    api.put_native_function(obj, u'generic', generic, 1)
    api.put_native_function(obj, u'specify', specify, 3)
    api.put_native_function(obj, u'clone', clone, 1)
    api.put_native_function(obj, u'trait', trait, 1)
    api.put_native_function(obj, u'attach', attach, -1)
    api.put_native_function(obj, u'detach', detach, -1)
    api.put_native_function(obj, u'set_traits', set_traits, 1)
    ## debugging
    # if not we_are_translated():
    #     api.put_native_function(obj, u'pypy_repr', pypy_repr)
    #     api.put_native_function(obj, u'inspect', inspect)


# 15.1.2.2

@complete_native_routine
def _id(routine):
    from rpython.rlib.objectmodel import compute_unique_id
    this = routine.get_arg(0)
    return str(hex(compute_unique_id(this)))


@complete_native_routine
def alert(routine):
    _print(routine)


@complete_native_routine
def _print(routine):
    args = routine._args.to_list()
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


def _eval(routine):
    from obin.objects.space import isstring
    from obin.runtime.routine import create_eval_routine

    x = routine.get_arg(0)

    assert isstring(x)

    src = api.to_native_string(x)
    from obin.compile.compiler import compile as cl
    code = cl(src)
    f = create_eval_routine(code)
    routine.call_routine(f)


@complete_native_routine
def coroutine(routine):
    from obin.objects.space import newcoroutine, isfunction
    fn = routine.get_arg(0)
    assert isfunction(fn)
    return newcoroutine(fn)


@complete_native_routine
def _range(routine):
    from obin.objects.space import newvector, newint
    start = routine.get_arg(0)
    end = routine.get_arg(1)
    start = api.to_native_integer(start)
    end = api.to_native_integer(end)
    items = [newint(i) for i in xrange(start, end)]
    return newvector(items)


@complete_native_routine
def generic(routine):
    from obin.objects.space import newgeneric
    name = routine.get_arg(0)
    return newgeneric(name)


@complete_native_routine
def specify(routine):
    method = routine.get_arg(0)
    signature = routine.get_arg(1)
    specification = routine.get_arg(2)
    method.reify_single(signature, specification)
    return None


@complete_native_routine
def clone(routine):
    origin = routine.get_arg(0)
    clone = api.clone(origin)
    return clone


@complete_native_routine
def traits(routine):
    from obin.objects.space import isobject
    obj = routine.get_arg(0)
    return api.traits(obj)

@complete_native_routine
def set_traits(routine):
    obj = routine.get_arg(0)
    traits = routine.get_arg(1)
    obj.set_traits(traits)
    return obj

@complete_native_routine
def attach(routine):
    args = routine.args().to_list()
    obj = routine.get_arg(0)
    for i in range(len(args) -1, 0, -1):
        trait = routine.get_arg(i)
        api.attach(obj, trait)
    return obj

@complete_native_routine
def detach(routine):
    args = routine.args().to_list()
    obj = routine.get_arg(0)
    for i in range(1, len(args)):
        trait = routine.get_arg(i)
        api.detach(obj, trait)

    return obj

@complete_native_routine
def kindof(routine):
    obj = routine.get_arg(0)
    trait = routine.get_arg(1)
    return api.kindof(trait, obj)


@complete_native_routine
def lookup(routine):
    this = routine.get_arg(0)
    key = routine.get_arg(1)
    default = routine.get_arg(2)
    return api.lookup_default(this, key, default)

@complete_native_routine
def clone(routine):
    this = routine.get_arg(0)
    return api.clone(this)

@complete_native_routine
def trait(routine):
    from obin.objects.space import newtrait
    name = routine.get_arg(0)
    return newtrait(name)
