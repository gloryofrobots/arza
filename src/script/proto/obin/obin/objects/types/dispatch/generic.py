from obin.objects.types.root import W_Root
from obin.runtime.exception import *
from obin.objects import api
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

    def create_dag(self, arity):
        dags = self._dags_
        count_dags = len(dags)

        index = arity + 1

        if index > count_dags:
            dags += [None] * (index - count_dags)

        dag = DAGRoot()
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

    def specify(self, signature, method):
        print "SPECIFY", signature
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

        dag = self.create_dag(arity)
        self.fill_dag(signatures, arity, dag)

    def _make_method_node(self, signatures):
        if len(signatures) != 1:
            raise ObinMethodSpecialisationError(self, u"Ambiguous method specialisation")

        sig = signatures[0]
        return [DAGMethodNode(sig.method)]

    def _make_nodes(self, index, arity, signatures, discriminators):
        if index == arity:
            leaf = self._make_method_node(signatures)
            print "METHOD", index, leaf
            return leaf

        groups = {}

        for signature in signatures:
            arg = signature.at(index)
            if not arg in groups:
                groups[arg] = [signature]
            else:
                groups[arg].append(signature)

        nodes = []
        from copy import copy
        for arg, group in groups.iteritems():
            d = arg.discriminator(discriminators)
            children = self._make_nodes(index + 1, arity, group, discriminators)
            nodes.append(DecisionNode(d, children))

        if index == 0:
            print ""
        print "NODES", index, nodes
        return nodes

    def fill_dag(self, signatures, arity, dag):
        dag.set_nodes(self._make_nodes(0, arity, signatures, dag.discriminators))
        print self._name_, dag


    def _add_method(self, m):
        index = len(self._methods_)
        self._methods_.append(m)
        return index

    def _specify_empty(self, method):
        idx = self._add_method(method)
        if self._signatures_[0] is not None:
            raise ObinMethodSpecialisationError(self, u"Specialisation for 0-length method has been already defined")

        self._signatures_[0] = idx

    def find_next_node(self, node, args, index):
        from obin.objects.object_space import object_space
        arg = args.at(index)
        traits = api.traits(arg)

        for trait in traits.values():
            next_node = node.lookup(trait)
            if next_node is not None:
                return next_node

        raise ObinMethodInvokeError(self, args)

    def lookup_method(self, args):
        arity = args.length()
        print "LOOKUP", self._name_, args, arity
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
        from obin.objects.object_space import object_space
        return object_space.traits.GenericTraits
