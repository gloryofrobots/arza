PRIMITIVES = [
    "IS", "NE", "EQ", "NOT", "ISNOT", "IN",
    "ADD", "MOD", "MUL", "DIV", "SUB",
    "UMINUS", "UPLUS", "GE", "GT", "LT", "LE",
    "BITNOT", "BITOR", "BITXOR", "BITAND",
    "LSH", "RSH", "URSH", 
    "__LENGTH__"
]
    
def gen_prim_ids():
    for i,n in enumerate(PRIMITIVES):
        print "%s = %d" % (n, i)

def gen_prims_repr():
    print "__PRIMITIVE_REPR__ = [None] * __LENGTH__"
    for p in PRIMITIVES[0:-1]:
        print "__PRIMITIVE_REPR__[%s] = %s" % (p, ("\"%s\"" % p))


def gen_prims_factory():

    S = \
"""
def newprimitives():
    P = [None] * __LENGTH__

""" 
    
    for p in PRIMITIVES[0:-1]:
        S += "    P[%s] = %s\n" % (p, ("primitive_%s" % p))

    S += "    return P\n"
    print S

def gen_prim_to_str():
    print \
"""
def primitive_to_str(p):
    return __PRIMITIVE_REPR__[p]\n\n
""" 

print "from obin.runtime.primitives.base import *"
print "\n# ********************  PRIMITIVES IDS ********************"
gen_prim_ids() 
print "\n\n# ********************* PRIMITIVES REPR ***************"
gen_prims_repr()
print
gen_prims_factory()
gen_prim_to_str()
