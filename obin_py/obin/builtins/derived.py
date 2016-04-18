from obin.types import space, api
from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error
from obin.types.space import newtuple as _t, newnativefunc as _f, newlist as _l


class Derive:
    def __init__(self):
        self.eq = False
        self.str = False
        self.repr = False
        self.indexed = False
        self.dict = False
        self.collection = False
        self.range = False


class Methods:
    def __init__(self, traits):
        self.at = self.find_method(u"at", traits.Collection)
        self.put = self.find_method(u"put", traits.Collection)
        self.del_ = self.find_method(u"del", traits.Collection)
        self.elem = self.find_method(u"elem", traits.Collection)

        self.len = self.find_method(u"len", traits.Sized)
        self.is_empty = self.find_method(u"is_empty", traits.Sized)

        self.equal = self.find_method(u"==", traits.Eq)
        self.index_of = self.find_method(u"index_of", traits.Indexed)

        self.str = self.find_method(u"str", traits.Str)
        self.repr = self.find_method(u"repr", traits.Repr)

        self.keys = self.find_method(u"keys", traits.Dict)
        self.values = self.find_method(u"values", traits.Dict)

        self.to_seq = self.find_method(u"to_seq", traits.Seqable)

    def find_method(self, name, trait):
        method = trait.find_method_by_name(space.newstring(name))
        if space.isvoid(method):
            return error.throw_2(error.Errors.RUNTIME_ERROR,
                                 space.newstring(u"Expected method %s of trait" % name),
                                 trait)
        return method


# Traits which can be derived
class Traits:
    def __init__(self):
        self.Str = None
        self.Repr = None
        self.Eq = None
        self.Indexed = None
        self.Dict = None
        self.Collection = None
        self.Sized = None
        self.Seq = None
        self.Seqable = None
        self.Range = None
        self.UnionDerived = None
        self.TypeDerived = None
        self.methods = None

    def _find_in(self, process, prelude, name):
        sym = space.newsymbol(process, name)
        if not api.contains(prelude, sym):
            error.throw_1(error.Errors.KEY_ERROR, space.newstring(u"Missing internal trait %s in prelude" % name))
        return api.at(prelude, sym)

    def find_trait(self, process, module, name):
        _trait = self._find_in(process, module, name)
        error.affirm_type(_trait, space.istrait)
        return _trait

    def find_type(self, process, module, name):
        _trait = self._find_in(process, module, name)
        error.affirm_type(_trait, space.isdatatype)
        return _trait

    def postsetup(self, process):
        from obin.runtime.load import import_module
        prelude = process.modules.prelude
        self.Str = self.find_trait(process, prelude, u"Str")
        self.Repr = self.find_trait(process, prelude, u"Repr")
        self.Eq = self.find_trait(process, prelude, u"Eq")
        self.Indexed = self.find_trait(process, prelude, u"Indexed")
        self.Dict = self.find_trait(process, prelude, u"Dict")
        self.Collection = self.find_trait(process, prelude, u"Collection")
        self.Sized = self.find_trait(process, prelude, u"Sized")
        self.Seq = self.find_trait(process, prelude, u"Seq")
        self.Seqable = self.find_trait(process, prelude, u"Seqable")
        self.Range = self.find_trait(process, prelude, u"Range")

        # GET MIXINS from datatype
        mixin_module = import_module(process, space.newsymbol(process, u"derive"))
        self.UnionDerived = self.find_type(process, mixin_module, u"UnionDerived")
        self.TypeDerived = self.find_type(process, mixin_module, u"TypeDerived")
        self.methods = Methods(self)
        self.postderive(process, prelude)
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1DATATYPE DERIVE"
        # self.postderive(process, mixin_module)

    def get_derived(self, _type):
        if space.isdatatype(_type):
            if _type.is_singleton:
                return self.get_derived_singleton(_type)
            else:
                return self.get_derived_default(_type)
        elif space.isunion(_type):
            return self.get_derived_union(_type)
        else:
            return error.throw_2(error.Errors.TYPE_ERROR, space.newstring(u"Type or Union Expected"), _type)

    def postderive(self, process, module):
        from obin.types import api, datatype
        symbols = module.symbols()
        for sym in symbols:
            obj = api.at(module, sym)
            if space.isextendable(obj):
                datatype.derive_default(process, obj)

    def get_derived_singleton(self, _type):
        impls = []
        impls.append(_l([self.Eq, self.TypeDerived]))
        impls.append(_l([self.Str, self.TypeDerived]))
        impls.append(_l([self.Repr, self.TypeDerived]))
        _type.derive.str = True
        _type.derive.repr = True
        _type.derive.eq = True
        return impls

    def get_derived_default(self, _type):
        impls = []
        impls.append(_l([self.Eq, self.TypeDerived]))
        impls.append(_l([self.Str, self.TypeDerived]))
        impls.append(_l([self.Repr, self.TypeDerived]))
        impls.append(_l([self.Collection, self.TypeDerived]))
        impls.append(_l([self.Sized, self.TypeDerived]))
        impls.append(_l([self.Indexed, self.TypeDerived]))
        impls.append(_l([self.Dict, self.TypeDerived]))

        _type.derive.str = True
        _type.derive.repr = True
        _type.derive.eq = True
        _type.derive.collection = True
        _type.derive.indexed = True
        _type.derive.dict = True
        return impls

    def get_derived_union(self, _type):
        impls = []
        impls.append(_l([self.Range, self.UnionDerived]))
        _type.derive.range = True
        return impls
