from obin.types import api, space
from obin.types.root import W_Any
from obin.types.space import isstring
from obin.utils.misc import is_absent_index
from obin.runtime import error


class References(object):
    _virtualizable2_ = ['_refs_[*]']
    _settled_ = True

    def __init__(self, env, size):
        self._refs_ = [None] * size
        self._resizable_ = not bool(size)
        self.env = env

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))

    def _get_refs(self, index):
        if index >= len(self._refs_):
            print "OLOLO"
        assert index < len(self._refs_)
        assert index >= 0

        if self._resizable_:
            self._resize_refs(index)

        return self._refs_[index]

    def _set_refs(self, index, value):
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def store_ref(self, symbol, index, value):
        ref = self._get_refs(index)

        if ref is not None:
            ref.put_value(value)
            return

        ref = self.env.get_reference(symbol)
        if not ref:
            return error.throw_1(error.Errors.REFERENCE, symbol)

        ref.put_value(value)
        self._set_refs(index, ref)

    def get_ref(self, symbol, index):
        # print "get_ref", symbol, index, self._refs_
        ref = self._get_refs(index)
        # print "ref", ref, ref is None
        if ref is None:
            ref = self.env.get_reference(symbol)
            # print " new ref", ref
            # assert ref is not None
            if not ref:
                return error.throw_1(error.Errors.REFERENCE, symbol)
            self._set_refs(index, ref)

        return ref.get_value()


class Reference:
    _immutable_fields_ = ['env', 'name', 'index']
    _settled_ = True

    def __init__(self, env, referenced, index):
        assert env is not None
        self.env = env
        self.name = referenced
        self.index = index

    def get_value(self):
        # print "Reference.ref_get_value", self.env, self.index
        return api.at_index(self.env, self.index)

    def put_value(self, value):
        api.put_at_index(self.env, self.index, value)


def get_reference(lex, identifier):
    # print "get_reference lex", lex
    if lex is None:
        return None

    index = api.get_index(lex, identifier)
    if not is_absent_index(index):
        ref = Reference(lex, identifier, index)
        return ref
    else:
        outer = lex.parent_env
        return get_reference(outer, identifier)


class W_Env(W_Any):
    _immutable_fields_ = ['binding_object', 'outer_environment']

    def __init__(self, obj, parent_environment):
        assert isinstance(parent_environment, W_Env) or parent_environment is None
        self.parent_env = parent_environment
        self.data = obj

    def get_reference(self, identifier):
        # print "Environment.get_reference"
        return get_reference(self.parent_env, identifier)

    def _behavior_(self, process):
        return process.std.behaviors.Environment

    def _put_at_index_(self, idx, v):
        api.put_at_index(self.data, idx, v)

    def _get_index_(self, n):
        return api.get_index(self.data, n)

    def _at_index_(self, i):
        return api.at_index(self.data, i)

    def _put_(self, k, v):
        assert space.issymbol(k)
        api.put(self.data, k, v)

    def _at_(self, n):
        assert space.issymbol(n)
        return api.at(self.data, n)

    def _tostring_(self):
        return self.data._tostring_()
