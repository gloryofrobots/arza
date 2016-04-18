from obin.types import space, api
from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error
from obin.types.space import newtuple as _t, newnativefunc as _f, newlist as _l


class Derive:
    def __init__(self):
        self.eq = False
        self.str = False
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
        self.Eq = None
        self.Indexed = None
        self.Dict = None
        self.Collection = None
        self.Sized = None
        self.Seq = None
        self.Seqable = None
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
        self.Eq = self.find_trait(process, prelude, u"Eq")
        self.Indexed = self.find_trait(process, prelude, u"Indexed")
        self.Dict = self.find_trait(process, prelude, u"Dict")
        self.Collection = self.find_trait(process, prelude, u"Collection")
        self.Sized = self.find_trait(process, prelude, u"Sized")
        self.Seq = self.find_trait(process, prelude, u"Seq")
        self.Seqable = self.find_trait(process, prelude, u"Seqable")
        self.Range = self.find_trait(process, prelude, u"Range")


        # GET MIXINS from datatype
        _datatype_ = import_module(process, space.newsymbol(process, u"datatype"))
        self.UnionDerived = self.find_type(process, _datatype_, u"UnionDerived")
        self.CoreMixin = self.find_type(process, _datatype_, u"CoreMixin")
        self.methods = Methods(self)

    def str_methods(self):
        return _l([
            _t([self.methods.str,
                _f(self.methods.str.name, str_, 1)
                ])
        ])

    def eq_methods(self):
        return _l([
            _t([self.methods.equal,
                _f(self.methods.equal.name, equal_, 2)
                ])
        ])

    def indexed_methods(self):
        return _l([
            _t([self.methods.index_of,
                _f(self.methods.index_of.name, index_of_, 2)
                ])
        ])

    def dict_methods(self):
        return _l([
            _t([self.methods.keys,
                _f(self.methods.keys.name, keys_, 1)
                ]),
            _t([self.methods.values,
                _f(self.methods.values.name, values_, 1)
                ])
        ])

    def sized_methods(self):
        return _l([
            _t([self.methods.len,
                _f(self.methods.len.name, len_, 1)
                ]),
            _t([self.methods.is_empty,
                _f(self.methods.is_empty.name, is_empty_, 1)
                ]),
        ])

    def collection_methods(self):
        return _l([
            _t([self.methods.at,
                _f(self.methods.at.name, at_, 2)
                ]),
            _t([self.methods.del_,
                _f(self.methods.del_.name, del_, 2)
                ]),
            _t([self.methods.elem,
                _f(self.methods.elem.name, elem_, 2)
                ]),
            _t([self.methods.put,
                _f(self.methods.put.name, put_, 3)
                ]),
        ])

    def derive_default_singleton(self, _type):
        impls = []
        impls.append(_l([self.Eq, self.eq_methods()]))
        impls.append(_l([self.Str, self.str_methods()]))

        _type.derive.str = True
        _type.derive.eq = True
        return impls

    def derive_default_union(self, _type):
        impls = []
        impls.append(_l([self.Range, self.UnionDerived]))
        _type.derive.range = True
        return impls

    def derive_default_record(self, _type):
        impls = []
        impls.append(_l([self.Eq, self.eq_methods()]))
        impls.append(_l([self.Str, self.str_methods()]))
        impls.append(_l([self.Collection, self.collection_methods()]))
        impls.append(_l([self.Sized, self.sized_methods()]))
        impls.append(_l([self.Indexed, self.indexed_methods()]))
        impls.append(_l([self.Dict, self.dict_methods()]))

        _type.derive.str = True
        _type.derive.eq = True
        _type.derive.collection = True
        _type.derive.indexed = True
        _type.derive.dict = True
        return impls

    def derive(self, _type, trait):
        impls = []
        if api.equal_b(self.Str, trait):
            _type.derive.str = True
            impls.append(_l([trait, self.str_methods()]))

        elif api.equal_b(self.Eq, trait):
            _type.derive.eq = True
            impls.append(_l([trait, self.eq_methods()]))

        elif api.equal_b(self.Indexed, trait):
            _type.derive.indexed = True
            _type.derive.collection = True
            if not _type.is_trait_implemented(self.Collection):
                impls.append(_l([self.Collection, self.collection_methods()]))
            if not _type.is_trait_implemented(self.Sized):
                impls.append(_l([self.Sized, self.sized_methods()]))
            impls.append(_l([trait, self.indexed_methods()]))

        elif api.equal_b(self.Dict, trait):
            _type.derive.dict = True
            _type.derive.collection = True
            if not _type.is_trait_implemented(self.Sized):
                impls.append(_l([self.Sized, self.sized_methods()]))
            if not _type.is_trait_implemented(self.Collection):
                impls.append(_l([self.Collection, self.collection_methods()]))

            impls.append(_l([trait, self.dict_methods()]))

        else:
            return error.throw_3(error.Errors.TRAIT_IMPLEMENTATION_ERROR,
                                 space.newstring(u"Trait is not derivable"), trait, _type)

        return _l(impls)


# Eq
@complete_native_routine
def equal_(process, routine):
    coll = routine.get_arg(0)
    other = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return api.equal(coll, other)


# Stringable
@complete_native_routine
def str_(process, routine):
    coll = routine.get_arg(0)
    error.affirm_type(coll, space.isrecord)
    return api.to_string(coll)


# Collection
@complete_native_routine
def len_(process, routine):
    coll = routine.get_arg(0)
    error.affirm_type(coll, space.isrecord)
    return api.length(coll)


@complete_native_routine
def is_empty_(process, routine):
    coll = routine.get_arg(0)
    error.affirm_type(coll, space.isrecord)
    return api.is_empty(coll)


@complete_native_routine
def put_(process, routine):
    key = routine.get_arg(0)
    value = routine.get_arg(1)
    coll = routine.get_arg(2)
    error.affirm_type(coll, space.isrecord)
    return api.put(coll, key, value)


@complete_native_routine
def at_(process, routine):
    key = routine.get_arg(0)
    coll = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return api.at(coll, key)


@complete_native_routine
def del_(process, routine):
    key = routine.get_arg(0)
    coll = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return api.delete(coll, key)


@complete_native_routine
def elem_(process, routine):
    key = routine.get_arg(0)
    coll = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return api.contains(coll, key)


# Associative
@complete_native_routine
def keys_(process, routine):
    coll = routine.get_arg(0)
    error.affirm_type(coll, space.isrecord)
    return coll.keys()


@complete_native_routine
def values_(process, routine):
    coll = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return coll.values()


# Indexed
@complete_native_routine
def index_of_(process, routine):
    obj = routine.get_arg(0)
    coll = routine.get_arg(1)
    error.affirm_type(coll, space.isrecord)
    return space.newint(coll.index_of(obj))


@complete_native_routine
def _union_range(process, routine):
    _from = routine.get_arg(0)
    _to = routine.get_arg(0)

"""
extend __UnionDerived__
    with Range
        def range _from  _to  ->
            union = _datatype:get_union _from
            if not (kindof _to union) ->
                throw ValueError("Invalid type for second argument", _to)
            else ->
                s1 = seq:drop_while (`!=` _from) (to_seq union)
                seq:take_while (`!=` _to) s1
        def range_from _from ->
            union = _datatype:get_union _from
            s1 = seq:drop_while (`!=` _from) (to_seq union)
        def range_from_by _from _by ->
            throw NotImplementedError ("Only range from Rangeable is supported")
        def range_by _from _to _by ->
            throw NotImplementedError ("Only range from Rangeable is supported")
            """