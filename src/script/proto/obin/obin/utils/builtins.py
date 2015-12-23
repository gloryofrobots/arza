from rpython.rlib.objectmodel import specialize, enforceargs, compute_unique_id, compute_identity_hash, r_dict

@specialize.argtype(0)
def ohash(obj):
    return compute_identity_hash(obj)

@specialize.argtype(0)
def oid(obj):
    return compute_unique_id(obj)

def _dict_key(obj1, obj2):
    v = obj1._equal_(obj2)
    # print "_dict_key", obj1, obj2, v
    return v

def _dict_hash(obj1):
    # print "_dict_hash", obj1,obj1._hash_()
    return obj1._hash_()

def odict():
    return r_dict(_dict_key, _dict_hash)


