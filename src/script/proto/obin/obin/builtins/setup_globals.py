# -*- coding: utf-8 -*-
from obin.runtime.routine import complete_native_routine
from obin.objects import api
from obin.objects import space
from rpython.rlib.rstring import UnicodeBuilder
from obin.runistr import encode_unicode_utf8



def setup(process, module, stdlib):
    ### Traits

    # THIS FUNCS NEED TO BE SIMPLE NATIVES FOR EACH TYPE (list_to_boolean, float_to_int, etc...)
    # self.ToBoolean = newgeneric(newstring(u"to_boolean"))
    # self.ToFloat = newgeneric(newstring(u"to_float"))
    # self.ToInteger = newgeneric(newstring(u"to_integer"))
    # self.ToList = newgeneric(newstring(u"to_list"))
    # self.ToTuple = newgeneric(newstring(u"to_tuple"))
    # self.ToMap = newgeneric(newstring(u"to_map"))
    # self.ToVector = newgeneric(newstring(u"to_vector"))
    # self.ToChar = newgeneric(newstring(u"to_character"))

    # 15.1.2.1
    api.put_primitive_function(module, u'eval', _eval, 1)
    api.put_primitive_function(module, u'print', _print, -1)
    api.put_primitive_function(module, u'@@', _print, -1)
    api.put_primitive_function(module, u'id', _id, 1)
    api.put_primitive_function(module, u'spawn_fiber', spawn_fiber, 0)
    api.put_primitive_function(module, u'activate_fiber', activate_fiber, 2)
    api.put_primitive_function(module, u'range', _range, 2)
    api.put_primitive_function(module, u'generic', generic, 1)
    api.put_primitive_function(module, u'specify', specify, 3)
    api.put_primitive_function(module, u'clone', clone, 1)
    api.put_primitive_function(module, u'trait', trait, 1)
    api.put_primitive_function(module, u'attach', attach, -1)
    api.put_primitive_function(module, u'detach', detach, -1)
    ## debugging
    # if not we_are_translated():
    #     api.put_native_function(obj, u'pypy_repr', pypy_repr)
    #     api.put_native_function(obj, u'inspect', inspect)


# 15.1.2.2

@complete_native_routine
def _id(process, routine):
    from rpython.rlib.objectmodel import compute_unique_id
    this = routine.get_arg(0)
    return space.newstring(unicode(hex(compute_unique_id(this))))



@complete_native_routine
def _print(process, routine):
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
    return space.newundefined()

def _eval(process, routine):
    from obin.runtime.environment import newenv
    from obin.compile import compiler
    x = routine.get_arg(0)

    assert space.isstring(x)

    src = api.to_native_string(x)
    source = compiler.compile_function_source(process, src, space.newstring(u"__eval__"))
    obj = source.code.scope.create_env_bindings()
    env = newenv(obj, None)
    func = space.newfunc(source.name, source.code, env)
    args = space.newemptyvector()
    api.call(process, func, args)


@complete_native_routine
def spawn_fiber(process, routine):
    from obin.objects.types.fiber import newfiber
    y1, y2 = newfiber(process)
    return space.newtuple([y1, y2])


def activate_fiber(process, routine):
    from obin.objects.types.fiber import activate_fiber as activate
    fiber = routine.get_arg(0)
    func = routine.get_arg(1)
    # args = routine.get_arg(2)
    args = space.newvector([])
    activate(process, fiber, func, args)
    return space.newundefined()


@complete_native_routine
def _range(process, routine):
    start = routine.get_arg(0)
    end = routine.get_arg(1)
    start = api.to_native_integer(start)
    end = api.to_native_integer(end)
    items = [space.newint(i) for i in xrange(start, end)]
    return space.newvector(items)


@complete_native_routine
def generic(process, routine):
    name = routine.get_arg(0)
    return space.newgeneric(name)


@complete_native_routine
def specify(process, routine):
    method = routine.get_arg(0)
    signature = routine.get_arg(1)
    specification = routine.get_arg(2)
    method.reify_single(signature, specification)
    return space.newundefined()


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
def attach(process, routine):
    args = routine.args().to_list()
    obj = routine.get_arg(0)
    for i in range(len(args) - 1, 0, -1):
        trait = routine.get_arg(i)
        api.attach(process, obj, trait)
    return obj


@complete_native_routine
def detach(process, routine):
    args = routine.args().to_list()
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
