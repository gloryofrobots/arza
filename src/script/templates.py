BUILTIN_MEHOD_TPL = """
OAny {{generic_name}}(OState* state{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %}) {
    {{ type }} method;
    method = _method(state, {{ args[0].name }}, {{ name }});

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "{{ name }} protocol not supported", {{ args[0].name }});
    }

    return method(state{% for arg in args %}, {{arg.name}}{% endfor %});
}"""

BUILTIN_MEHOD_TPL_DECLARATION = """
OAny {{generic_name}}(OState* state{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %});
"""

METHOD_IMPLEMENTATION_DECLARATION = """
OAny {{name}}(OState* state{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %});
"""


BEHAVIOR_TPL = """
typedef struct _OBehavior {
    obin_string __name__;
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