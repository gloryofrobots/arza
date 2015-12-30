class Generics:
    def __init__(self):
        from obin.objects.space import newgeneric, newstring
        self.Length = newgeneric(newstring(u"length"))
        self.Add = newgeneric(newstring(u"__add__"))
        self.Sub = newgeneric(newstring(u"__sub__"))
        self.Mul = newgeneric(newstring(u"__mul__"))
        self.Div = newgeneric(newstring(u"__div__"))
        self.Mod = newgeneric(newstring(u"__mod__"))
        self.Equal = newgeneric(newstring(u"__equal__"))
        self.Compare = newgeneric(newstring(u"__compare__"))
        self.GreaterThen = newgeneric(newstring(u"__gt__"))
        self.GreaterEqual = newgeneric(newstring(u"__ge__"))
        self.UnaryMinus = newgeneric(newstring(u"__unary_minus__"))
        self.UnaryPlus = newgeneric(newstring(u"__unary_plus__"))
        self.BitNot = newgeneric(newstring(u"__bitnot__"))
        self.BitOr = newgeneric(newstring(u"__bitor__"))
        self.BitXor = newgeneric(newstring(u"__bitxor__"))
        self.BitAnd = newgeneric(newstring(u"__bitand__"))
        self.LeftShift = newgeneric(newstring(u"__left_shift__"))
        self.RightShift = newgeneric(newstring(u"__right_shift__"))
        self.UnsignedRightShift = newgeneric(newstring(u"__unsigned_right_shift__"))


class Traits:
    def __init__(self):
        from obin.objects.space import newtrait, newtraits, newstring
        self.Any = newtrait(newstring(u"Any"))
        self.Boolean = newtrait(newstring(u"Boolean"))

        self.True = newtrait(newstring(u"True"))
        self.TrueTraits = newtraits([self.True, self.Boolean, self.Any])

        self.False = newtrait(newstring(u"False"))
        self.FalseTraits = newtraits([self.False, self.Boolean, self.Any])

        self.Nil = newtrait(newstring(u"Nil"))
        self.NilTraits = newtraits([self.Nil, self.Any])

        self.Undefined = newtrait(newstring(u"Undefined"))
        self.UndefinedTraits = newtraits([self.Undefined, self.Any])

        self.Char = newtrait(newstring(u"Char"))
        self.CharTraits = newtraits([self.Char, self.Any])

        self.Number = newtrait(newstring(u"Number"))
        self.Integer = newtrait(newstring(u"Integer"))
        self.IntegerTraits = newtraits([self.Integer, self.Number, self.Any])

        self.Float = newtrait(newstring(u"Float"))
        self.FloatTraits = newtraits([self.Float, self.Number, self.Any])

        self.Symbol = newtrait(newstring(u"Symbol"))
        self.SymbolTraits = newtraits([self.Symbol, self.Any])

        self.String = newtrait(newstring(u"String"))
        self.StringTraits = newtraits([self.String, self.Any])

        self.List = newtrait(newstring(u"List"))

        self.Vector = newtrait(newstring(u"Vector"))
        self.VectorTraits = newtraits([self.Vector, self.Any])

        self.Tuple = newtrait(newstring(u"Tuple"))
        self.TupleTraits = newtraits([self.Tuple, self.Any])

        self.Function = newtrait(newstring(u"Function"))
        self.FunctionTraits = newtraits([self.Function, self.Any])

        self.Coroutine = newtrait(newstring(u"Coroutine"))
        self.CoroutineTraits = newtraits([self.Coroutine, self.Function, self.Any])

        self.Generic = newtrait(newstring(u"Generic"))
        self.GenericTraits = newtraits([self.Generic, self.Function, self.Any])

        self.Primitive = newtrait(newstring(u"Primitive"))
        self.PrimitiveTraits = newtraits([self.Primitive, self.Function, self.Any])

        self.Object = newtrait(newstring(u"Object"))
        self.ObjectTraits = newtraits([self.Object, self.Any])

        self.Module = newtrait(newstring(u"Object"))
        self.ModuleTraits = newtraits([self.Module, self.Any])


class StdLib:
    def __init__(self):
        self.traits = Traits()
        self.generics = Generics()


