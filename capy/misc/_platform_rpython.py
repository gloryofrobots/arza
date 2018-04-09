from rpython.rlib.objectmodel import (specialize, enforceargs,
                                      compute_unique_id, compute_identity_hash,
                                      always_inline)
from rpython.rlib.rrandom import Random
from rpython.rlib import rarithmetic, runicode, rstring, rfloat
from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib import jit
from rpython.rlib import streamio
from rpython.rlib.objectmodel import r_dict
# import rpython.rlib.rsre.rsre_re as re
import re

r = Random()

NOT_FOUND = -1


def random():
    return r.random()


@always_inline
@enforceargs(int)
def is_absent_index(idx):
    return idx == NOT_FOUND


@always_inline
def absent_index():
    return NOT_FOUND


@specialize.argtype(0)
def arza_hash(obj):
    return compute_identity_hash(obj)


@specialize.argtype(0)
def arza_id(obj):
    return compute_unique_id(obj)
