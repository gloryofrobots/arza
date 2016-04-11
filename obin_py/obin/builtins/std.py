from obin.types import api, space, plist, datatype
from obin.runtime import error
from obin.builtins import derived


class Types:
    def __init__(self, symbols):
        from obin.types.space import newnativedatatype as newtype
        _s = symbols.symbol
        # ---------------AUTOGENERATED---------------------
        self.Bool = newtype(_s(u"Bool"))
        self.Char = newtype(_s(u"Char"))
        self.Int = newtype(_s(u"Int"))
        self.Float = newtype(_s(u"Float"))
        self.Symbol = newtype(_s(u"Symbol"))
        self.String = newtype(_s(u"String"))
        self.List = newtype(_s(u"List"))
        self.Vector = newtype(_s(u"Vector"))
        self.Tuple = newtype(_s(u"Tuple"))
        self.Map = newtype(_s(u"Map"))
        self.Function = newtype(_s(u"Function"))
        self.Generic = newtype(_s(u"Generic"))
        self.Method = newtype(_s(u"Method"))
        self.NativeFunction = newtype(_s(u"NativeFunction"))
        self.Fiber = newtype(_s(u"Fiber"))
        self.Trait = newtype(_s(u"Trait"))
        self.Datatype = newtype(_s(u"Datatype"))
        self.LazyVal = newtype(_s(u"LazyVal"))
        self.Env = newtype(_s(u"Env"))

    # def derive_single(self):
    #
    # def postsetup(self, process, traits):
    #
    #     pass



class Std:
    def __init__(self, symbols):
        self.types = Types(symbols)
        self.traits = derived.Traits()
        self.initialized = False

    def postsetup(self, process):
        self.traits.postsetup(process)
        self.initialized = True
