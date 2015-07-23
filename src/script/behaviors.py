class Method(object):
    def __init__(self, name, arity,  methodType=None):
        self.name = name
        self.arity = arity
        if not methodType:
            self.methodType = 'obin_func_%d' % self.arity
        else:
            self.methodType = methodType

__destroy__ = Method('__destroy__', 1, "obin_destructor")
__mark__ = Method('__mark__', 1, "obin_each")

__tostring__ = Method('__tostring__', 1)
__tobool__ = Method('__tobool__', 1)
__clone__ = Method('__clone__', 1)
__compare__ = Method('__compare__', 2)
__hash__ = Method('__hash__', 1)

__iterator__ = Method('__iterator__', 1)
__length__ = Method('__length__', 1)
__getitem__ = Method('__getitem__', 2)
__hasitem__ = Method('__hasitem__', 2)
__delitem__ = Method('__delitem__', 2)
__setitem__ = Method('__setitem__', 3)


__next__ = Method('__next__', 1)

__tointeger__ = Method('__tointeger__', 1)
__tofloat__ = Method('__tofloat__', 1)
__topositive__ = Method('__topositive__', 1)
__tonegative__ = Method('__tonegative__', 1)

BEHAVIOR_PARTS = [
        {
            'name':'MEMORY',
            'methods': [__destroy__, __mark__]
        },
        {
            'name':'BASE',
            'methods': [__tostring__, __tobool__, __clone__, __compare__, __hash__]
        },
        {
            'name':'COLLECTION',
            'methods': [
              __iterator__, __length__, __getitem__, __hasitem__, __delitem__, __setitem__
            ]
        },
        {
            'name':'GENERATOR',
            'methods': [
               __next__ 
            ]
        }, 
        {
            'name':'NUMBER_CAST',
            'methods': [
                __tointeger__, __tofloat__, __topositive__, __tonegative__
            ]
        }, 
         {
            'name':'NUMBER_OPERATIONS',
            'methods': [
                Method('__abs__', 1),
                Method('__invert__', 1),

                Method('__add__', 2),
                Method('__subtract__', 2),
                Method('__divide__', 2),
                Method('__multiply__', 2),
                Method('__pow__', 2),
                Method('__leftshift__', 2),
                Method('__rightshift__', 2),
                Method('__mod__', 2),
                Method('__and__', 2),
                Method('__or__', 2),
                Method('__xor__', 2),
            ]
        }, 
]

def write_behavior_h(filename):
    f = open(filename, "w+")
    BEHAVIOR = ""
    BEHAVIOR_TPL__ = """
typedef struct _ObinBehavior {
    obin_string __name__;
%s
} ObinBehavior;
    """
    BEHAVIOR_DEF_TPL = """
#define OBIN_BEHAVIOR_DEFINE(structname, name, %s)  \\ 
static ObinBehavior structname = { \\ 
    name, %s  \\ 
};"""

    BEHAVIOR_DECL_TPL = """
#define OBIN_BEHAVIOR_DECLARE(structname) \
static ObinBehavior structname;"""

    MACROS_BODY = []
    BEHAVIOR_BODY = []
    for part in BEHAVIOR_PARTS:
        BEHAVIOR_BODY.append("    /*%s*/" % part['name'])
        MACROSES = []
        for method in part['methods']:
            BEHAVIOR_BODY.append("    %s %s;" % (method.methodType, method.name))
            MACROSES.append(method.name)
        MACROS_NAME = "#define OBIN_BEHAVIOR_%s" % part['name']
        MACROS = "%s(%s)  %s \n" %(MACROS_NAME, ",".join(MACROSES), ", ".join(MACROSES))
        MACROS_BODY.append(MACROS)

        MACROS_NAME = "#define OBIN_BEHAVIOR_%s_NULL" % part['name']
        MACROS = "%s %s " %(MACROS_NAME, ", ".join(['0']*len(part['methods'])))
        MACROS_BODY.append(MACROS)



    BEHAVIOR = BEHAVIOR_TPL__ % "\n".join(BEHAVIOR_BODY)
    f.write(BEHAVIOR + "\n")

    MACROS = "\n".join(MACROS_BODY)
    f.write(MACROS + "\n")

    f.write(BEHAVIOR_DECL_TPL + "\n")

    names = [part['name'] for part in BEHAVIOR_PARTS]
    BEHAVIOR_DEF = BEHAVIOR_DEF_TPL % (", ".join(names), ", ".join(names))
    f.write(BEHAVIOR_DEF + "\n")

write_behavior_h('behavior.h')