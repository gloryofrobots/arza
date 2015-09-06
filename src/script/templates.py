BUILTIN_MEHOD_TPL = """
OAny {{generic_name}}(OState* S{% for arg in args %}, {{arg.type}} {{arg.name}}{% endfor %}) {
    {{ type }} method;
    method = _method(S, {{ args[0].name }}, {{ name }});
    {% if isMutator %}
    _CHECK_FROZEN(S, {{ args[0].name }});
    {% endif %}
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

ARRAY_PACK_TPL = """
OAny {{name}}(OState* S, omem_t size, ...){
    ObinArray * self;
    omem_t i;
    {{type}} item;
    va_list vargs;

    if(size == 0) {
        return _obin_array_empty(S);
    }

    if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
        return oraise(S, oerrors(S)->TypeError,
                "Array invalid size", OInteger(size));
    }

    self = _obin_array_new(S , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
        item = va_arg(vargs, {{type}});
        self->data[i] = {{constructor}};
    }
    va_end(vargs);

    return OArray_make(self);
}
"""