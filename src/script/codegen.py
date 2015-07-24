def write_builtin_c(filename):
    from behavior import BEHAVIOR
    import templates as tpls
    from jinja2 import Template
    template = Template(tpls.BUILTIN_MEHOD_TPL)
    f = open(filename, "w+")
    
    def write_methods(methods):
        f.write("\n/************************* %s **********************************/\n" % methods.name)

        results = []
        for method in methods:
            data = template.render(method.as_dict())
            results.append(data)
        
        f.write("\n".join(results))
        f.write("\n")

    for methods in BEHAVIOR[1:]:
        write_methods(methods)
    
def write_builtin_h(filename):
    from behavior import BEHAVIOR
    import templates as tpls
    from jinja2 import Template
    template = Template(tpls.BUILTIN_MEHOD_TPL_DECLARATION)
    f = open(filename, "w+")
    def write_methods(methods):
        f.write("\n/************************* %s **********************************/\n" % methods.name)

        results = []
        for method in methods:
            data = template.render(method.as_dict())
            results.append(data)
        
        f.write("\n".join(results))
        f.write("\n")

    for methods in BEHAVIOR[1:]:
        write_methods(methods)


def write_behavior_h(filename):
    from behavior import BEHAVIOR
    import templates as tpls
    f = open(filename, "w+")
   
    MACROS_BODY = []
    BEHAVIOR_BODY = []
    for part in BEHAVIOR:
        BEHAVIOR_BODY.append("    /*%s*/" % part.name)
        MACROSES = []
        for method in part.methods:
            BEHAVIOR_BODY.append("    %s %s;" % (method.type, method.name))
            MACROSES.append(method.name)
        MACROS_NAME = "#define OBIN_BEHAVIOR_%s" % part.name
        MACROS = "%s(%s)  %s \n" %(MACROS_NAME, ",".join(MACROSES), ", ".join(MACROSES))
        MACROS_BODY.append(MACROS)

        MACROS_NAME = "#define OBIN_BEHAVIOR_%s_NULL" % part.name
        MACROS = "%s %s " %(MACROS_NAME, ", ".join(['0']*len(part.methods)))
        MACROS_BODY.append(MACROS)

    f.write(tpls.BEHAVIOR_TPL % "\n".join(BEHAVIOR_BODY) + "\n")

    MACROS = "\n".join(MACROS_BODY)
    f.write(MACROS + "\n")

    f.write(tpls.BEHAVIOR_DECL_TPL + "\n")

    names = [part.name for part in BEHAVIOR]
    BEHAVIOR_DEF = tpls.BEHAVIOR_DEF_TPL % (", ".join(names), ", ".join(names))
    f.write(BEHAVIOR_DEF + "\n")

write_behavior_h('generated/behavior.h')

write_builtin_h("generated/builtin.h")
write_builtin_c("generated/_builtin.c")