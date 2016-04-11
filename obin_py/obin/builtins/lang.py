from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error
from obin.types import api, space, plist, environment, datatype, tuples

from obin.runistr import encode_unicode_utf8
from obin.misc.platform import rstring, compute_unique_id
from obin.misc import fs
from obin.compile import compiler

# TODO MAKE IT obin:is_seq ...
from obin.builtins import lang_names


def put_lang_func(process, module, name, func, arity):
    name_without_prefix = name.replace(lang_names.PREFIX, "")
    api.put_native_function(process, module, unicode(name), func, arity)
    api.put_native_function(process, module, unicode(name_without_prefix), func, arity)


def setup(process, module, stdlib):
    api.put_native_function(process, module, u'eval', _eval, 1)
    api.put_native_function(process, module, u'print', _print, -1)
    api.put_native_function(process, module, u'id', _id, 1)
    api.put_native_function(process, module, u'apply', apply, 2)
    api.put_native_function(process, module, u'concat', concat_tuples, 2)
    api.put_native_function(process, module, u'time', time, 0)
    api.put_native_function(process, module, u'traits', traits, 1)
    api.put_native_function(process, module, u'get_type', _type, 1)
    api.put_native_function(process, module, u'range', _range, 2)
    api.put_native_function(process, module, u'lazyval', _lazyval, 1)
    put_lang_func(process, module, lang_names.NOT, __not, 1)
    put_lang_func(process, module, lang_names.IS_INDEXED, is_indexed, 1)
    put_lang_func(process, module, lang_names.IS_SEQ, is_seq, 1)
    put_lang_func(process, module, lang_names.IS_DICT, is_map, 1)
    put_lang_func(process, module, lang_names.IS, __is, 2)
    put_lang_func(process, module, lang_names.ISNOT, __isnot, 2)
    put_lang_func(process, module, lang_names.KINDOF, __kindof, 2)
    put_lang_func(process, module, lang_names.TYPE, __type, 3)
    put_lang_func(process, module, lang_names.UNION, __union, 2)
    put_lang_func(process, module, lang_names.METHOD, __method, 4)
    put_lang_func(process, module, lang_names.TRAIT, __trait, 3)
    put_lang_func(process, module, lang_names.IMPLEMENT, __implement, 3)
    put_lang_func(process, module, lang_names.EXTEND, __extend, 2)
    put_lang_func(process, module, lang_names.DERIVE, __derive, 2)
    put_lang_func(process, module, lang_names.PARTIAL, __partial, 1)

    put_lang_func(process, module, u"vector", __vector, -1)

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
def __vector(process, routine):
    args = routine._args.to_l()
    return space.newpvector(args)


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
        return error.throw_1(error.Errors.TYPE_ERROR, space.newstring(u"arguments tuple expected"))
    api.call(process, func, args)


@complete_native_routine
def _type(process, routine):
    left = routine.get_arg(0)
    return api.get_type(process, left)


@complete_native_routine
def _lazyval(process, routine):
    left = routine.get_arg(0)
    error.affirm_type(left, space.isfunction)
    return space.newlazyval(left)


@complete_native_routine
def __not(process, routine):
    left = routine.get_arg(0)
    error.affirm_type(left, space.isboolean)
    return api.not_(left)


# CURRENTLY NOT USED
@complete_native_routine
def __module(process, routine):
    source = routine.get_arg(0)
    # fenv opcode
    env = routine.get_arg(1)
    m = environment.create_environment(process, source, env)
    return m


@complete_native_routine
def __type(process, routine):
    name = routine.get_arg(0)
    fields = routine.get_arg(1)
    constructor = routine.get_arg(2)
    _datatype = space.newdatatype(process, name, fields, constructor)
    return _datatype


@complete_native_routine
def __union(process, routine):
    name = routine.get_arg(0)
    types = routine.get_arg(1)
    error.affirm_type(name, space.issymbol)
    error.affirm_type(types, space.islist)
    error.affirm_iterable(types, space.isdatatype)
    union = space.newunion(process, name, types)
    return union


@complete_native_routine
def __method(process, routine):
    _trait = routine.get_arg(0)
    name = routine.get_arg(1)
    signature = routine.get_arg(2)
    impl = routine.get_arg(3)
    method = space.newmethod_default_implementation(name, _trait, signature, impl)
    return method


@complete_native_routine
def __trait(process, routine):
    name = routine.get_arg(0)
    varname = routine.get_arg(1)
    constraints = routine.get_arg(2)
    if space.istuple(constraints):
        constraints = tuples.to_list(constraints)
    _trait = space.newtrait(name, varname, constraints)
    return _trait


@complete_native_routine
def __derive(process, routine):
    _traits = routine.get_arg(0)
    _types = routine.get_arg(1)
    for t in _types:
        datatype.derive_traits(process, t, _traits)

    return space.newbool(True)


@complete_native_routine
def __implement(process, routine):
    _trait = routine.get_arg(0)
    _type = routine.get_arg(1)
    _impls = routine.get_arg(2)
    _type = datatype.implement_trait(_type, _trait, _impls)
    return _type


@complete_native_routine
def __extend(process, routine):
    _type = routine.get_arg(0)
    _traits = routine.get_arg(1)
    _type = datatype.extend_type(_type, _traits)
    return _type


@complete_native_routine
def __partial(process, routine):
    func = routine.get_arg(0)
    return space.newpartial(func)


@complete_native_routine
def concat_tuples(process, routine):
    from obin.types.tuples import concat
    v1 = routine.get_arg(0)
    v2 = routine.get_arg(1)
    return concat(v1, v2)


@complete_native_routine
def time(process, routine):
    import time
    return space.newfloat(time.time())


@complete_native_routine
def is_indexed(process, routine):
    v1 = routine.get_arg(0)
    if not space.istuple(v1) and not space.isarguments(v1):
        return space.newbool(False)
    return space.newbool(True)


@complete_native_routine
def is_seq(process, routine):
    from obin.types.space import islist, newbool
    v1 = routine.get_arg(0)
    if islist(v1):
        return newbool(True)
    if api.kindof_b(process, v1, process.std.traits.Seq):
        return newbool(True)

    return newbool(False)


@complete_native_routine
def is_map(process, routine):
    v1 = routine.get_arg(0)
    if not space.ispmap(v1):
        return space.newbool(False)
    return space.newbool(True)


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
