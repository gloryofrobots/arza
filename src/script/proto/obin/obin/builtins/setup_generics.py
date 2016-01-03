from obin.runtime.routine import complete_native_routine
from obin.objects import api
from obin.objects import space
from rpython.rlib.rstring import UnicodeBuilder
from obin.runistr import encode_unicode_utf8

def setup(process, module, stdlib):
    _install(process, module, stdlib)
    _reify(process, module, stdlib)

def _install(process, module, stdlib):

    generics = stdlib.generics
    # AUTIGENERATED generic_gen.py
    api.put(module, generics.Add.name, generics.Add)
    api.put(module, generics.Sub.name, generics.Sub)
    api.put(module, generics.Mul.name, generics.Mul)
    api.put(module, generics.Div.name, generics.Div)
    api.put(module, generics.Mod.name, generics.Mod)
    api.put(module, generics.UnaryPlus.name, generics.UnaryPlus)
    api.put(module, generics.UnaryMinus.name, generics.UnaryMinus)
    api.put(module, generics.Not.name, generics.Not)
    api.put(module, generics.Equal.name, generics.Equal)
    api.put(module, generics.NotEqual.name, generics.NotEqual)
    api.put(module, generics.Compare.name, generics.Compare)
    api.put(module, generics.In.name, generics.In)
    api.put(module, generics.GreaterThen.name, generics.GreaterThen)
    api.put(module, generics.GreaterEqual.name, generics.GreaterEqual)
    api.put(module, generics.BitNot.name, generics.BitNot)
    api.put(module, generics.BitOr.name, generics.BitOr)
    api.put(module, generics.BitXor.name, generics.BitXor)
    api.put(module, generics.BitAnd.name, generics.BitAnd)
    api.put(module, generics.LeftShift.name, generics.LeftShift)
    api.put(module, generics.RightShift.name, generics.RightShift)
    api.put(module, generics.UnsignedRightShift.name, generics.UnsignedRightShift)
    api.put(module, generics.Length.name, generics.Length)
    api.put(module, generics.Str.name, generics.Str)


def _reify(process, module, stdlib):
    import obin.builtins.internals.wrappers as wrappers
    from obin.objects.types.dispatch.generic import reify_single
    from obin.objects.space import newtuple, newprimitive, newstring
    generics = stdlib.generics
    traits = stdlib.traits

    reify_single(process, generics.Add,
                 newtuple([traits.Integer, traits.Integer]),
                 newprimitive(newstring(u"add_i_i"), wrappers.builtin_add_i_i, 2))
