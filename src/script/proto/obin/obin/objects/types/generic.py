from root import W_Root
from obin.runtime.exception import *
from obin.objects import api

class LookupLeaf(object):
    def __init__(self, idx):
        self.method_index = idx

    def __str__(self):
        return "{Leaf %d}" % self.method_index

    def __repr__(self):
        return "{Leaf %d}" % self.method_index


class LookupNode(object):
    def __init__(self):
        self.children = {}

    def lookup(self, arg):
        return self.children.get(arg, None)

    def lookup_or_insert(self, trait):
        node = self.children.get(trait, None)

        if not node:
            node = LookupNode()
            self.insert(trait, node)

        return node

    def insert(self, trait, node):
        self.children[trait] = node
        return node

    def __str__(self):
        return "Node %s" % str(self.children)



class W_Generic(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ["_name_"]

    def __init__(self, name):
        super(W_Generic, self).__init__()
        self._name_ = name
        self._methods_ = []
        self._signatures_ = []

    def specify(self, signature, method):
        arity = signature.length()
        signatures = self._signatures_
        count_signatures = len(signatures)

        if arity != method.arity:
            raise ObinMethodSpecialisationError(self, u"Method arity doesn't match implementation function")

        if arity == 0:
            return self._specify_empty(method)

        index = arity + 1

        if index > count_signatures:
            signatures += [None] * (index - count_signatures)

        node = signatures[arity]

        if not node:
            node = LookupNode()
            signatures[arity] = node

        self._specify(node, signature, method)

        print str(node)

    def _add_method(self, m):
        index = len(self._methods_)
        self._methods_.append(m)
        return index

    def _specify_empty(self, method):
        idx = self._add_method(method)
        if self._signatures_[0] is not None:
            raise ObinMethodSpecialisationError(self, u"Specialisation for 0-length method has been already defined")

        self._signatures_[0] = idx

    def _specify(self, root_node, signature, method):
        index = 0
        length = signature.length()
        max_index = length - 1
        node = root_node

        # make path for method
        while index < max_index:
            arg = signature.at(index)
            trait = api.totrait(arg)
            node = node.lookup_or_insert(trait)
            index += 1

        # here we set method to leaf of hash table tree
        last_arg = signature.at(max_index)
        trait = api.totrait(last_arg)

        if node.lookup(trait):
            raise ObinMethodSpecialisationError(self, u"Method for such signature has been already defined")

        method_idx = self._add_method(method)
        node.insert(trait, LookupLeaf(method_idx))

    def find_next_node(self, node, args, index):
        from obin.objects.object_space import object_space
        arg = args.at(index)
        traits = api.traits(arg)

        for trait in traits.values():
            next_node = node.lookup(trait)
            if next_node is not None:
                return next_node

        raise ObinMethodInvokeError(self, arg)

    def lookup_method(self, args):

        arity = args.length()
        if arity == 0:
            idx = self._signatures_[0]
            return self._methods_[idx]

        node = self._signatures_[arity]
        index = 0
        max_index = arity - 1

        while index < max_index:
            node = self.find_next_node(node, args, index)
            index += 1

        leaf = self.find_next_node(node, args, max_index)
        return self._methods_[leaf.method_index]

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
