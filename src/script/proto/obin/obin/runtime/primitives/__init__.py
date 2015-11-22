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
ISA = 24
__LENGTH__ = 25


# ********************* PRIMITIVES REPR ***************
__REPR__ = [None] * __LENGTH__
__REPR__[IS] = "IS"
__REPR__[NE] = "NE"
__REPR__[EQ] = "EQ"
__REPR__[NOT] = "NOT"
__REPR__[ISNOT] = "ISNOT"
__REPR__[IN] = "IN"
__REPR__[ADD] = "ADD"
__REPR__[MOD] = "MOD"
__REPR__[MUL] = "MUL"
__REPR__[DIV] = "DIV"
__REPR__[SUB] = "SUB"
__REPR__[UMINUS] = "UMINUS"
__REPR__[UPLUS] = "UPLUS"
__REPR__[GE] = "GE"
__REPR__[GT] = "GT"
__REPR__[LT] = "LT"
__REPR__[LE] = "LE"
__REPR__[BITNOT] = "BITNOT"
__REPR__[BITOR] = "BITOR"
__REPR__[BITXOR] = "BITXOR"
__REPR__[BITAND] = "BITAND"
__REPR__[LSH] = "LSH"
__REPR__[RSH] = "RSH"
__REPR__[URSH] = "URSH"
__REPR__[ISA] = "ISA"


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
    P[ISA] = primitive_ISA
    return P


def primitive_to_str(p):
    return __REPR__[p]
