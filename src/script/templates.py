BUILTIN_MEHOD_TPL = """
OAny {{generic_name}}(OState* S{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %}) {
    {{ type }} method;
    method = _method(S, {{ args[0].name }}, {{ name }});

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "{{ name }} protocol not supported", {{ args[0].name }});
    }

    return method(S{% for arg in args %}, {{arg.name}}{% endfor %});
}"""

BUILTIN_MEHOD_TPL_DECLARATION = """
OAny {{generic_name}}(OState* S{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %});
"""

METHOD_IMPLEMENTATION_DECLARATION = """
static OAny {{name}}(OState* S{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %});
"""


BEHAVIOR_TPL = """
typedef struct _OBehavior {
    ostring __name__;
%s
} OBehavior;
    """

BEHAVIOR_DEF_TPL = """
#define OBEHAVIOR_DEFINE(structname, name, %s)  \\ 
static OBehavior structname = { \\ 
    name, %s  \\ 
};"""

BEHAVIOR_DECL_TPL = """
#define OBEHAVIOR_DECLARE(structname) \
static OBehavior structname;"""