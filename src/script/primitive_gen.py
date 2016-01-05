PRIMITIVES = [
    "IS", "NE", "EQ", "NOT", "ISNOT", "IN",
    "ADD", "MOD", "MUL", "DIV", "SUB",
    "UMINUS", "UPLUS", "GE", "GT", "LT", "LE",
    "BITNOT", "BITOR", "BITXOR", "BITAND",
    "LSH", "RSH", "URSH", "CONS",
    "__LENGTH__"
]
    
def gen_prim_ids():
    for i,n in enumerate(PRIMITIVES):
        print "%s = %d" % (n, i)

def gen_prims_repr():
    print "__INTERNALS_REPR__ = [None] * __LENGTH__"
    for p in PRIMITIVES[0:-1]:
        print "__INTERNALS_REPR__[%s] = %s" % (p, ("\"%s\"" % p))


def gen_prims_factory():

    S = \
"""
def newinternals():
    P = [None] * __LENGTH__

""" 
    
    for p in PRIMITIVES[0:-1]:
        S += "    P[%s] = %s\n" % (p, ("internal_%s" % p))

    S += "    return P\n"
    S += "\n\n__INTERNALS__ = newinternals()"
    print S

def gen_prim_to_str():
    print \
"""
def internal_to_str(p):
    return __INTERNALS_REPR__[p]\n\n
""" 

print "from obin.runtime.primitives.base import *"
print "\n# ********************  INTERNALS IDS ********************"
gen_prim_ids() 
print "\n\n# ********************* INTERNALS REPR ***************"
gen_prims_repr()
print
gen_prims_factory()
gen_prim_to_str()

print """
def get_internal(id):
    return __INTERNALS__[id]
"""