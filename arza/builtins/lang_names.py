from arza.types import space
PREFIX = "arza:"
PREFIXU = u"arza:"

NOT = PREFIX + "not"
HAS = PREFIX + "has"
IS = PREFIX + "is"
IS_EMPTY = PREFIX + "is_empty"
LOAD_MODULE = PREFIX + "load_module"

ISNOT = PREFIX + "isnot"
KINDOF = PREFIX + "kindof"
IS_IMPLEMENTED = PREFIX + "isimplemented"

# functions used by compiler in code gen
DESCRIBE = PREFIX + "describe"
IS_INDEXED = PREFIX + "is_indexed"
IS_TUPLE = PREFIX + "is_tuple"
IS_SEQ = PREFIX + "is_seq"
IS_DICT = PREFIX + "is_dict"
LEN = PREFIX + "len"
TYPE = PREFIX + "deftype"
GENERIC = PREFIX + "defgeneric"
INTERFACE = PREFIX + "definterface"

LENSE = PREFIX + "lense"

CURRY = PREFIX + "curry"

SPECIFY = PREFIX + "specify"
OVERRIDE = PREFIX + "override"
OVERRIDE_HELPER = PREFIX + "__override__"
RECEIVE_HELPER = PREFIX + "__receive__"

AFFIRM_TYPE_DECORATOR = PREFIX + "__affirm_type_decorator__"

AT = PREFIX + "at"
PUT = PREFIX + "put"
PUT_DEFAULT = PREFIX + "put_default"

DROP = PREFIX + "drop"
TAKE = PREFIX + "take"
REST = PREFIX + "rest"
FIRST = PREFIX + "first"
CONS = PREFIX + "cons"

EQ = PREFIX + "=="
GE = PREFIX + ">="

HOLE_PREFIX = "@__hole__"
RANDOM_TRAIT_NAME_PREFIX = "@__trait__"
RANDOM_TYPE_DEC_NAME_PREFIX = "@__type_dec__"

TO_SEQ = PREFIX + "to_seq"
CONCAT = PREFIX + "++"
APPLY = PREFIX + "apply"
NEGATE = PREFIX + "negate"
CAST = PREFIX + "cast"


TINT = PREFIX + "Int"
TFLOAT = PREFIX + "Float"
TBOOL = PREFIX + "Bool"
TCHAR = PREFIX + "Char"
TSYMBOL = PREFIX + "Symbol"
TSTRING = PREFIX + "String"
TLIST = PREFIX + "List"
TTUPLE = PREFIX + "Tuple"
TMAP = PREFIX + "Map"
TANY = PREFIX + "Any"
TRECORD = PREFIX + "Record"
TABSTRACT = PREFIX + "Abstract"
TDATATYPE = PREFIX + "Datatype"

SVALUEOF = "VALUEOF"

SKIP_ON_AUTO_EXPORT_START = "_"
SKIP_ON_AUTO_EXPORT_MIDDLE = ":"


def get_lang_symbol(process, suffix):
    assert isinstance(suffix, unicode)
    name = PREFIXU + suffix
    return space.newsymbol(process, name)



