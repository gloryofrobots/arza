from root import W_Root
from obin.runtime.exception import *
from obin.objects import api

class W_MultiMethod(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ["_name_"]

    def __init__(self, name):
        super(W_MultiMethod, self).__init__()
        self._name_ = name
        self._methods_ = []

    def specify(self, signature, method):
        signature = signature.values()
        arity = len(signature)
        assert arity == method.arity
        methods = self._methods_
        count_methods = len(methods)
        if arity > count_methods:
            methods += [None] * (arity - count_methods)

        record = methods[arity-1]
        if not record:
            methods[arity-1] = []

        record = methods[arity-1]
        record.insert(0, [signature, method])

    @staticmethod
    def match_signature(signature, args):
        l_args = len(args)
        l_sig = len(signature)
        assert l_args == l_sig

        for i in range(l_args):
            sig = signature[i]
            arg = args[i]

            if not arg.kindof(sig):
                return False

        return True

    def lookup_method(self, args):
        args = args.values()

        arity = len(args)
        record = self._methods_[arity-1]
        for data in record:
            signature = data[0]
            if self.match_signature(signature, args):
                return data[1]

        raise ObinMethodInvokeError(self._name_, args)

    def _tostring_(self):
        return "method %s {}" % self._name_.value()

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from obin.objects.object_space import object_space
        return api.at(object_space.traits.Function, k)

    def _call_(self, routine, args):
        assert routine
        method = self.lookup_method(args)
        routine.process.call_object(method, routine, args)
