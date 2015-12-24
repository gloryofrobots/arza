from rpython.rlib.objectmodel import (specialize, enforceargs,
                                      compute_unique_id, compute_identity_hash, r_dict,
                                      always_inline)
from obin.objects.space import isany

NOT_FOUND = -1


@always_inline
@enforceargs(int)
def is_absent_index(idx):
    return idx == NOT_FOUND


@always_inline
def absent_index():
    return NOT_FOUND


@specialize.argtype(0)
def ohash(obj):
    return compute_identity_hash(obj)


@specialize.argtype(0)
def oid(obj):
    return compute_unique_id(obj)


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


def odict():
    return r_dict(_dict_key, _dict_hash)
