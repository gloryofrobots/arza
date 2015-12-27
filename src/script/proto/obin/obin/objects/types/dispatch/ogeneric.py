from obin.objects.types.oroot import W_Root
from obin.objects.space import newtuple, isany
from obin.runtime.error import *
from signature import newsignature, new_base_signature
from obin.objects import api
from dag import *


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
    from rpython.rlib.objectmodel import r_dict
    return r_dict(_dict_key, _dict_hash)


class W_Generic(W_Root):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name):
        self.name = name
        self.methods = []
        self.dags = []
        self.signatures = []

    def _tostring_(self):
        return "method %s {}" % api.to_native_string(self.name)

    def _tobool_(self):
        return True

    def _call_(self, process, args):
        method = _lookup_method(process, self, args)
        process.call_object(method, args)

    def _traits_(self, process):
        return process.stdlib.traits.GenericTraits


def reify(process, gf, signatures):
    modified = {}

    for sig in signatures:
        args_signature = api.at_index(sig, 0)
        method = api.at_index(sig, 1)
        signature = newsignature(process, args_signature, method)
        arity = signature.arity

        if arity != method.arity:
            raise ObinMethodSpecialisationError(gf, u"Method arity doesn't match implementation function")

        if arity == 0:
            return _specify_empty(gf, method)
        try:
            signatures = modified[arity]
        except KeyError:
            signatures = _get_signatures(gf, arity)
            modified[arity] = signatures

        index = _find_signature_index(gf, signatures, signature)
        if index != -1:
            old = signatures[index]
            _remove_method(gf, old.method)
            signatures[index] = signature
        else:
            signatures.append(signature)

        _add_method(gf, method)

    for arity, signatures in modified.iteritems():
        _create_dag(gf, signatures, arity)


def reify_single(process, gf, signature, method):
    reify(process, gf,
          newtuple(
              [newtuple([signature, method])]))


"""
##########################################################
"""


def _create_dag(gf, signatures, arity):
    dags = gf.dags
    count_dags = len(dags)

    index = arity + 1

    if index > count_dags:
        dags += [None] * (index - count_dags)

    discriminators = []
    nodes = _make_nodes(gf, 0, arity, signatures, discriminators)
    dag = RootNode(nodes, discriminators)
    # print "DAG for", gf._name_
    # print dag
    dags[arity] = dag
    return dag


def _get_signatures(gf, arity):
    signatures = gf.signatures
    count_signatures = len(signatures)

    index = arity + 1

    if index > count_signatures:
        signatures += [None] * (index - count_signatures)

    record = signatures[arity]

    if not record:
        record = []
        signatures[arity] = record

    return record


def _find_signature_index(gf, signatures, signature):
    for i, sig in enumerate(signatures):
        if signature.equal(sig):
            return i

    return -1


def _make_method_node(gf, signatures):
    if len(signatures) != 1:
        raise ObinMethodSpecialisationError(gf, u"Ambiguous method specialisation")

    sig = signatures[0]
    return [LeafNode(sig.method)]


def _make_nodes(gf, index, arity, signatures, discriminators):
    if index == arity:
        leaf = _make_method_node(gf, signatures)
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
        children = _make_nodes(gf, index + 1, arity, group, discriminators)
        if len(children) == 1:
            nodes.append(SingleNode(d, children[0]))
        else:
            nodes.append(GroupNode(d, children))

    # print "NODES", index, nodes
    return nodes


def _add_method(gf, m):
    index = len(gf.methods)
    gf.methods.append(m)
    return index


def _remove_method(gf, m):
    gf.methods.remove(m)


def _specify_empty(gf, method):
    _add_method(gf, method)
    if gf.signatures[0] is not None:
        raise ObinMethodSpecialisationError(gf, u"Specialisation for 0-length method has been already defined")

    # Storing dummy signature here for rpython translation
    gf.signatures[0] = [new_base_signature(method)]


def _lookup_method(process, gf, args):
    arity = api.n_length(args)
    # print "LOOKUP", gf._name_, args, arity
    if arity == 0:
        sig = gf.signatures[0][0]
        return sig.method

    if arity >= len(gf.dags):
        raise ObinMethodInvokeError(gf, args)

    dag = gf.dags[arity]
    method = dag.evaluate(process, args)
    if not method:
        raise ObinMethodInvokeError(gf, args)

    return method


if __name__ == "__main__":
    from tests import test_3, test_any

    test_3()
    test_any()
