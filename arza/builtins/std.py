from arza.types import api, space, plist
from arza.runtime import error


def find_in_module(process, prelude, name):
    sym = space.newsymbol(process, name)
    if not api.contains(prelude, sym):
        error.throw_1(error.Errors.KEY_ERROR, space.newstring(u"Missing internal trait %s in prelude" % name))
    return api.at(prelude, sym)


class Types:
    def __init__(self, symbols):
        # from arza.types.space import newnativedatatype as newtype
        from arza.types.space import newabstractdatatype as newtype
        _s = symbols.symbol

        self.Any = newtype(_s(u"Any"), space.newunit())
        self.Abstract = newtype(_s(u"Abstract"), self.Any)
        self.Record = newtype(_s(u"Record"), self.Any)
        # ---------------AUTOGENERATED---------------------

        self.Bool = newtype(_s(u"Bool"), self.Any)

        self.Char = newtype(_s(u"Char"), self.Any)

        self.Number = newtype(_s(u"Number"), self.Any)

        self.Int = newtype(_s(u"Int"), self.Number)

        self.Float = newtype(_s(u"Float"), self.Number)

        self.Symbol = newtype(_s(u"Symbol"), self.Any)

        self.String = newtype(_s(u"String"), self.Any)

        self.List = newtype(_s(u"List"), self.Any)

        self.Vector = newtype(_s(u"Vector"), self.Any)

        self.Tuple = newtype(_s(u"Tuple"), self.Any)

        self.Map = newtype(_s(u"Map"), self.Any)

        self.Function = newtype(_s(u"Function"), self.Any)

        self.Partial = newtype(_s(u"Partial"), self.Any)

        self.Generic = newtype(_s(u"Generic"), self.Any)

        self.FiberChannel = newtype(_s(u"FiberChannel"), self.Any)

        self.Coroutine = newtype(_s(u"Coroutine"), self.Any)

        self.Interface = newtype(_s(u"Interface"), self.Any)

        self.Datatype = newtype(_s(u"Datatype"), self.Any)

        self.Env = newtype(_s(u"Env"), self.Any)

        self.Array = newtype(_s(u"Array"), self.Any)

        self.AssocArray = newtype(_s(u"AssocArray"), self.Any)

        self.PID = newtype(_s(u"PID"), self.Any)

        self.Module = newtype(_s(u"Module"), self.Any)


class Functions:
    def __init__(self):
        self.call = None

    def setup(self, process):
        prelude = process.modules.prelude
        self.call = self.find_function(process, prelude, u"call")

    def find_function(self, process, module, name):
        _fun = find_in_module(process, module, name)
        error.affirm_type(_fun, space.isfunction)
        return _fun


class Interfaces:
    def __init__(self, symbols):
        _s = symbols.symbol
        self.Seq = None
        self.Dict = None
        self.Indexed = None
        self.Len = None
        self.Indexed = None
        self.Eq = None
        self.Repr = None
        self.Call = None
        self.instance_derived = None
        self.singleton_derived = None

    def setup(self, process):
        prelude = process.modules.prelude
        self.Seq = self.find_interface(process, prelude, u"Seq")
        self.Dict = self.find_interface(process, prelude, u"Dict")
        self.Indexed = self.find_interface(process, prelude, u"Indexed")
        self.Len = self.find_interface(process, prelude, u"Len")
        self.Eq = self.find_interface(process, prelude, u"Eq")
        self.Repr = self.find_interface(process, prelude, u"Repr")
        self.Call = self.find_interface(process, prelude, u"Call")

        self.instance_derived = space.newlist([
            self.Dict, self.Len, self.Indexed,
            self.Eq, self.Repr
        ])

        self.singleton_derived = space.newlist([
            self.Eq, self.Repr
        ])

        self._derive_prelude(process)

    def _derive_prelude(self, process):
        module = process.modules.prelude
        from arza.types import api, datatype
        symbols = module.symbols()
        for sym in symbols:
            obj = api.at(module, sym)
            if space.isuserdatatype(obj):
                derived = self.get_derived(obj)
                datatype.derive(process, obj, derived)

    def get_derived(self, _type):
        if space.isuserdatatype(_type):
            if space.isabstracttype(_type):
                return self.singleton_derived
            else:
                return self.instance_derived
        else:
            return error.throw_2(error.Errors.TYPE_ERROR, space.newstring(u"Type Expected"), _type)

    def is_default_derivable_interface(self, iface):
        return api.contains_b(self.instance_derived, iface) or api.contains_b(self.singleton_derived, iface)

    def find_interface(self, process, module, name):
        _interface = find_in_module(process, module, name)
        error.affirm_type(_interface, space.isinterface)
        return _interface


class Std:
    def __init__(self, symbols):
        self.functions = Functions()
        self.interfaces = Interfaces(symbols)
        self.types = Types(symbols)
        self.initialized = False

    def postsetup(self, process):
        self.interfaces.setup(process)
        self.functions.setup(process)
        self.initialized = True
