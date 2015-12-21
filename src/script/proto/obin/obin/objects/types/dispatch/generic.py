from obin.objects.types.root import W_Root
from obin.runtime.exception import *
from signature import Signature
from dag import *


class W_Generic(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ["_name_"]

    def __init__(self, name):
        super(W_Generic, self).__init__()
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

    def reify(self, signatures):
        modified = {}

        for sig in signatures:
            args_signature = sig.at(0)
            method = sig.at(1)
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

            try:
                index = signatures.index(signature)
                old = signatures[index]
                self._methods_.remove(old.method)
                signatures[index] = signature
            except ValueError:
                signatures.append(signature)

            self._methods_.append(method)

        for arity, signatures in modified.iteritems():
            self.create_dag(signatures, arity)

    def reify_single(self, signature, method):
        # print "SPECIFY", signature
        arity = signature.length()

        if arity != method.arity:
            raise ObinMethodSpecialisationError(self, u"Method arity doesn't match implementation function")

        if arity == 0:
            return self._specify_empty(method)

        signatures = self.get_signatures(arity)

        signature = Signature(signature, method)

        # replace old method with same signature
        try:
            index = signatures.index(signature)
            old = signatures[index]
            self._methods_.remove(old.method)
            signatures[index] = signature
        except ValueError:
            signatures.append(signature)

        self._methods_.append(method)

        self.create_dag(signatures, arity)

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

        groups = {}
        for signature in signatures:
            arg = signature.at(index)
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
        idx = self._add_method(method)
        if self._signatures_[0] is not None:
            raise ObinMethodSpecialisationError(self, u"Specialisation for 0-length method has been already defined")

        self._signatures_[0] = idx

    def lookup_method(self, args):
        arity = args.length()
        # print "LOOKUP", self._name_, args, arity
        if arity == 0:
            idx = self._signatures_[0]
            return self._methods_[idx]

        if arity >= len(self._dags_):
            raise ObinMethodInvokeError(self, args)

        dag = self._dags_[arity]
        method = dag.evaluate(args)
        if not method:
            raise ObinMethodInvokeError(self, args)

        return method

    def _tostring_(self):
        return "method %s {}" % self._name_.value()

    def _tobool_(self):
        return True

    def _call_(self, routine, args):
        assert routine
        method = self.lookup_method(args)
        routine.process.call_object(method, routine, args)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.GenericTraits


from tests import test_3, test_any

test_3()
test_any()
