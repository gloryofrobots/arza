BUILTIN_MEHOD_TPL = """
ObinAny {{generic_name}}(ObinState* state{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %}) {
    {{ type }} method;
    method = _method(state, any, {{ name }});

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "{{ name }} protocol not supported", self);
    }

    return method(state{% for arg in args %}, {{arg.name}}{% endfor %});
}"""

BEHAVIOR_TPL = """
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