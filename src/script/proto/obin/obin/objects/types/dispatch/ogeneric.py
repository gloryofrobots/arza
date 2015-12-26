from obin.objects.types.oroot import W_Root
from obin.objects.types import otuple
from obin.objects.space import newtuple, isany
from obin.runtime.exception import *
from signature import Signature, BaseSignature
from obin.objects import api
from dag import *
from rpython.rlib.objectmodel import r_dict

class SrategyType:
    ARITY_DISPATCH = 0
    SINGLE_DISPATCH = 1
    MULTIPLE_DISPATCH = 2

def _dict_key(obj1, obj2):
    assert isany(obj1)
    assert isany(obj2)
    v = obj1._equal_(obj2)
    # print "_dict_key", obj1, obj2, v
    return v


def _dict_hash(obj1):
    assert isany(obj1)
    # print "_dict_hash", obj1,obj1._hash_()
    return obj1._hash_()


def group_dict():
    return r_dict(_dict_key, _dict_hash)

class W_Generic(W_Root):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name):
        self._name_ = name
        self._methods_ = []
        self._dags_ = []
        self._signatures_ = []

    def create_dag(self, signatures, arity):
        dags = self._dags_
        count_dags = len(dags)

        index = arity + 1

        if index > count_dags:
            dags += [None] * (index - count_dags)

        discriminators = []
        nodes = self._make_nodes(0, arity, signatures, discriminators)
        dag = RootNode(nodes, discriminators)
        # print "DAG for", self._name_
        # print dag
        dags[arity] = dag
        return dag

    def get_signatures(self, arity):
        signatures = self._signatures_
        count_signatures = len(signatures)

        index = arity + 1

        if index > count_signatures:
            signatures += [None] * (index - count_signatures)

        record = signatures[arity]

        if not record:
            record = []
            signatures[arity] = record

        return record

    def find_signature_index(self, signatures, signature):
        for i, sig in enumerate(signatures):
            if signature.equal(sig):
                return i

        return -1

    def reify(self, signatures):
        modified = {}

        for sig in signatures:
            args_signature = api.at_index(sig, 0)
            method = api.at_index(sig, 1)
            signature = Signature(args_signature, method)
            arity = signature.arity

            if arity != method.arity:
                raise ObinMethodSpecialisationError(self, u"Method arity doesn't match implementation function")

            if arity == 0:
                return self._specify_empty(method)
            try:
                signatures = modified[arity]
            except KeyError:
                signatures = self.get_signatures(arity)
                modified[arity] = signatures

            index = self.find_signature_index(signatures, signature)
            if index != -1:
                old = signatures[index]
                self._methods_.remove(old.method)
                signatures[index] = signature
            else:
                signatures.append(signature)

            self._methods_.append(method)

        for arity, signatures in modified.iteritems():
            self.create_dag(signatures, arity)

    def reify_single(self, signature, method):
        self.reify(
                newtuple(
                    [newtuple([signature, method])]))

    def _make_method_node(self, signatures):
        if len(signatures) != 1:
            raise ObinMethodSpecialisationError(self, u"Ambiguous method specialisation")

        sig = signatures[0]
        return [LeafNode(sig.method)]

    def _make_nodes(self, index, arity, signatures, discriminators):
        if index == arity:
            leaf = self._make_method_node(signatures)
            # print "METHOD", index, leaf
            return leaf

        groups = group_dict()
        for signature in signatures:
            arg = signature.get_argument(index)
            if arg not in groups:
                groups[arg] = [signature]
            else:
                groups[arg].append(signature)

        nodes = []
        for arg, group in groups.iteritems():
            d = arg.discriminator(discriminators)
            children = self._make_nodes(index + 1, arity, group, discriminators)
            if len(children) == 1:
                nodes.append(SingleNode(d, children[0]))
            else:
                nodes.append(GroupNode(d, children))

        # print "NODES", index, nodes
        return nodes

    def _add_method(self, m):
        index = len(self._methods_)
        self._methods_.append(m)
        return index

    def _specify_empty(self, method):
        self._add_method(method)
        if self._signatures_[0] is not None:
            raise ObinMethodSpecialisationError(self, u"Specialisation for 0-length method has been already defined")

        self._signatures_[0] = [BaseSignature(method)]

    def lookup_method(self, args):
        arity = api.n_length(args)
        # print "LOOKUP", self._name_, args, arity
        if arity == 0:
            sig = self._signatures_[0][0]
            return sig.method

        if arity >= len(self._dags_):
            raise ObinMethodInvokeError(self, args)

        dag = self._dags_[arity]
        method = dag.evaluate(args)
        if not method:
            raise ObinMethodInvokeError(self, args)

        return method

    def _tostring_(self):
        return "method %s {}" % api.to_native_string(self._name_)

    def _tobool_(self):
        return True

    def _call_(self, process, args):
        method = self.lookup_method(args)
        process.call_object(method, args)

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.GenericTraits

if __name__ == "__main__":
    from tests import test_3, test_any
    test_3()
    test_any()
