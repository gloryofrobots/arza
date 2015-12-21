from obin.runtime.primitives.base import *

# ********************  PRIMITIVES IDS ********************
IS = 0
NE = 1
EQ = 2
NOT = 3
ISNOT = 4
IN = 5
ADD = 6
MOD = 7
MUL = 8
DIV = 9
SUB = 10
UMINUS = 11
UPLUS = 12
GE = 13
GT = 14
LT = 15
LE = 16
BITNOT = 17
BITOR = 18
BITXOR = 19
BITAND = 20
LSH = 21
RSH = 22
URSH = 23
__LENGTH__ = 24


# ********************* PRIMITIVES REPR ***************
__PRIMITIVE_REPR__ = [None] * __LENGTH__
__PRIMITIVE_REPR__[IS] = "IS"
__PRIMITIVE_REPR__[NE] = "NE"
__PRIMITIVE_REPR__[EQ] = "EQ"
__PRIMITIVE_REPR__[NOT] = "NOT"
__PRIMITIVE_REPR__[ISNOT] = "ISNOT"
__PRIMITIVE_REPR__[IN] = "IN"
__PRIMITIVE_REPR__[ADD] = "ADD"
__PRIMITIVE_REPR__[MOD] = "MOD"
__PRIMITIVE_REPR__[MUL] = "MUL"
__PRIMITIVE_REPR__[DIV] = "DIV"
__PRIMITIVE_REPR__[SUB] = "SUB"
__PRIMITIVE_REPR__[UMINUS] = "UMINUS"
__PRIMITIVE_REPR__[UPLUS] = "UPLUS"
__PRIMITIVE_REPR__[GE] = "GE"
__PRIMITIVE_REPR__[GT] = "GT"
__PRIMITIVE_REPR__[LT] = "LT"
__PRIMITIVE_REPR__[LE] = "LE"
__PRIMITIVE_REPR__[BITNOT] = "BITNOT"
__PRIMITIVE_REPR__[BITOR] = "BITOR"
__PRIMITIVE_REPR__[BITXOR] = "BITXOR"
__PRIMITIVE_REPR__[BITAND] = "BITAND"
__PRIMITIVE_REPR__[LSH] = "LSH"
__PRIMITIVE_REPR__[RSH] = "RSH"
__PRIMITIVE_REPR__[URSH] = "URSH"


def newprimitives():
    P = [None] * __LENGTH__

    P[IS] = primitive_IS
    P[NE] = primitive_NE
    P[EQ] = primitive_EQ
    P[NOT] = primitive_NOT
    P[ISNOT] = primitive_ISNOT
    P[IN] = primitive_IN
    P[ADD] = primitive_ADD
    P[MOD] = primitive_MOD
    P[MUL] = primitive_MUL
    P[DIV] = primitive_DIV
    P[SUB] = primitive_SUB
    P[UMINUS] = primitive_UMINUS
    P[UPLUS] = primitive_UPLUS
    P[GE] = primitive_GE
    P[GT] = primitive_GT
    P[LT] = primitive_LT
    P[LE] = primitive_LE
    P[BITNOT] = primitive_BITNOT
    P[BITOR] = primitive_BITOR
    P[BITXOR] = primitive_BITXOR
    P[BITAND] = primitive_BITAND
    P[LSH] = primitive_LSH
    P[RSH] = primitive_RSH
    P[URSH] = primitive_URSH
    return P


def primitive_to_str(p):
    return __PRIMITIVE_REPR__[p]
