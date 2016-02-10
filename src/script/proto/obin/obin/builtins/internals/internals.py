
# ********************  INTERNALS IDS ********************
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
CONS = 24
NOTIN = 25
NOTA = 26
ISA = 27
KINDOF = 28
__LENGTH__ = 29


# ********************* INTERNALS REPR ***************
__INTERNALS_REPR__ = [None] * __LENGTH__
__INTERNALS_REPR__[IS] = "IS"
__INTERNALS_REPR__[NE] = "NE"
__INTERNALS_REPR__[EQ] = "EQ"
__INTERNALS_REPR__[NOT] = "NOT"
__INTERNALS_REPR__[ISNOT] = "ISNOT"
__INTERNALS_REPR__[IN] = "IN"
__INTERNALS_REPR__[ADD] = "ADD"
__INTERNALS_REPR__[MOD] = "MOD"
__INTERNALS_REPR__[MUL] = "MUL"
__INTERNALS_REPR__[DIV] = "DIV"
__INTERNALS_REPR__[SUB] = "SUB"
__INTERNALS_REPR__[UMINUS] = "UMINUS"
__INTERNALS_REPR__[UPLUS] = "UPLUS"
__INTERNALS_REPR__[GE] = "GE"
__INTERNALS_REPR__[GT] = "GT"
__INTERNALS_REPR__[LT] = "LT"
__INTERNALS_REPR__[LE] = "LE"
__INTERNALS_REPR__[BITNOT] = "BITNOT"
__INTERNALS_REPR__[BITOR] = "BITOR"
__INTERNALS_REPR__[BITXOR] = "BITXOR"
__INTERNALS_REPR__[BITAND] = "BITAND"
__INTERNALS_REPR__[LSH] = "LSH"
__INTERNALS_REPR__[RSH] = "RSH"
__INTERNALS_REPR__[URSH] = "URSH"
__INTERNALS_REPR__[CONS] = "CONS"
__INTERNALS_REPR__[NOTIN] = "NOTIN"
__INTERNALS_REPR__[NOTA] = "NOTA"
__INTERNALS_REPR__[ISA] = "ISA"
__INTERNALS_REPR__[KINDOF] = "KINDOF"


def newinternals():
    P = [None] * __LENGTH__

    P[IS] = internal_IS
    P[NE] = internal_NE
    P[EQ] = internal_EQ
    P[NOT] = internal_NOT
    P[ISNOT] = internal_ISNOT
    P[IN] = internal_IN
    P[ADD] = internal_ADD
    P[MOD] = internal_MOD
    P[MUL] = internal_MUL
    P[DIV] = internal_DIV
    P[SUB] = internal_SUB
    P[UMINUS] = internal_UMINUS
    P[UPLUS] = internal_UPLUS
    P[GE] = internal_GE
    P[GT] = internal_GT
    P[LT] = internal_LT
    P[LE] = internal_LE
    P[BITNOT] = internal_BITNOT
    P[BITOR] = internal_BITOR
    P[BITXOR] = internal_BITXOR
    P[BITAND] = internal_BITAND
    P[LSH] = internal_LSH
    P[RSH] = internal_RSH
    P[URSH] = internal_URSH
    P[CONS] = internal_CONS
    P[NOTIN] = internal_NOTIN
    P[NOTA] = internal_NOTA
    P[ISA] = internal_ISA
    P[KINDOF] = internal_KINDOF
    return P


__INTERNALS__ = newinternals()


def internal_to_str(p):
    return __INTERNALS_REPR__[p]


def get_internal(id):
    return __INTERNALS__[id]
