from rpython.rlib.objectmodel import (specialize, enforceargs,
                                      compute_unique_id, compute_identity_hash,
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


