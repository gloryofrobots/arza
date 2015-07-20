
BEHAVIOR_PARTS = [
        {
            'name':'MEMORY',
            'methods': [
                {'type':'obin_destructor', 'name':'__destroy__'},
                {'type':'obin_func_1_func_1', 'name':'__mark__'},
            ]
        },
        {
            'name':'BASE',
            'methods': [
                {'type':'obin_func_1', 'name':'__tostring__'},
                {'type':'obin_func_1', 'name':'__tobool__'},
                {'type':'obin_func_1', 'name':'__clone__'},
                {'type':'obin_func_2', 'name':'__compare__'},
                {'type':'obin_func_1', 'name':'__hash__'},
            ]
        },
        {
            'name':'COLLECTION',
            'methods': [
                {'type':'obin_func_1', 'name':'__iterator__'},
                {'type':'obin_func_1', 'name':'__length__'},
                {'type':'obin_func_2', 'name':'__getitem__'},
                {'type':'obin_func_3', 'name':'__setitem__'},
                {'type':'obin_func_2', 'name':'__hasitem__'},
                {'type':'obin_func_2', 'name':'__delitem__'},
            ]
        },
        {
            'name':'GENERATOR',
            'methods': [
                {'type':'obin_func_1', 'name':'__next__'},
            ]
        }, 
        {
            'name':'NUMBER',
            'methods': [
                {'type':'obin_func_1', 'name':'__tointeger__'},
                {'type':'obin_func_2', 'name':'__add__'},
            ]
        }, 
]

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
};
"""

BEHAVIOR_DECL_TPL = """
#define OBIN_BEHAVIOR_DECLARE(structname) \
static ObinBehavior structname;
"""

MACROS_BODY = []
BEHAVIOR_BODY = []
for part in BEHAVIOR_PARTS:
    BEHAVIOR_BODY.append("    /*%s*/" % part['name'])
    MACROSES = []
    for method in part['methods']:
        BEHAVIOR_BODY.append("    %s %s;" % (method['type'], method['name']))
        MACROSES.append(method['name'])
    MACROS_NAME = "#define OBIN_BEHAVIOR_%s" % part['name']
    MACROS = "%s(%s)  %s \n" %(MACROS_NAME, ",".join(MACROSES), ", ".join(MACROSES))
    MACROS_BODY.append(MACROS)

    MACROS_NAME = "#define OBIN_BEHAVIOR_%s_NULL" % part['name']
    MACROS = "%s %s \n" %(MACROS_NAME, ", ".join(['0']*len(part['methods'])))
    MACROS_BODY.append(MACROS)



BEHAVIOR = BEHAVIOR_TPL__ % "\n".join(BEHAVIOR_BODY)
print BEHAVIOR

MACROS = "\n".join(MACROS_BODY)
print MACROS

print BEHAVIOR_DECL_TPL

names = [part['name'] for part in BEHAVIOR_PARTS]
BEHAVIOR_DEF = BEHAVIOR_DEF_TPL % (", ".join(names), ", ".join(names))
print BEHAVIOR_DEF