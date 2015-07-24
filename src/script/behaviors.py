class Arg(object):
    def __init__(self, name):
        self.name = name
        self.type = "ObinAny"
    pass

class Method(object):
    def __init__(self, name, arity,  methodType=None):
        self.name = name
        self.arity = arity
        if not methodType:
            self.type = 'obin_func_%d' % self.arity
        else:
            self.type = methodType
        
        self.args = [Arg("self")]
        for i in range(1, self.arity):
            self.args.append(Arg("arg%d" % i))

        name = self.name.replace("__", "")
        self.generic_name = "obin_%s" % name

    def as_dict(self):
        return self.__dict__

class Methods(object):
    def __init__(self, name, *methods):
        self.name = name
        self.methods = methods

    def __iter__(self):
        return self.methods.__iter__()

__MEMORY__ = Methods("MEMORY", 
    Method('__destroy__', 1, "obin_destructor"),
    Method('__mark__', 1, "obin_each")
    )

__BASE__ = Methods("BASE", 
    Method('__tostring__', 1),
    Method('__tobool__', 1),
    Method('__clone__', 1),
    Method('__compare__', 2),
    Method('__hash__', 1),
    )

__COLLECTION__ = Methods("COLLECTION", 
    Method('__iterator__', 1),
    Method('__length__', 1),
    Method('__getitem__', 2),
    Method('__hasitem__', 2),
    Method('__delitem__', 2),
    Method('__setitem__', 3),
    )

__GENERATOR__ = Methods("GENERATOR", Method('__next__', 1))

__NUMBER_CAST__ = Methods("NUMBER_CAST", 
     Method('__tointeger__', 1),
     Method('__tofloat__', 1),
     Method('__topositive__', 1),
     Method('__tonegative__', 1),
    )

__NUMBER_OPERATIONS__ = Methods("NUMBER_OPERATIONS", 
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
    )


BEHAVIOR_PARTS = [
__MEMORY__,__BASE__, __COLLECTION__, __GENERATOR__, __NUMBER_CAST__, __NUMBER_OPERATIONS__
]


def write_builtin_c(filename):
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
        
    for methods in BEHAVIOR_PARTS[1:]:
        write_methods(methods)
    


def write_behavior_h(filename):
    import templates as tpls
    f = open(filename, "w+")
    BEHAVIOR = ""
    MACROS_BODY = []
    BEHAVIOR_BODY = []
    for part in BEHAVIOR_PARTS:
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



    BEHAVIOR = tpls.BEHAVIOR_TPL % "\n".join(BEHAVIOR_BODY)
    f.write(BEHAVIOR + "\n")

    MACROS = "\n".join(MACROS_BODY)
    f.write(MACROS + "\n")

    f.write(tpls.BEHAVIOR_DECL_TPL + "\n")

    names = [part.name for part in BEHAVIOR_PARTS]
    BEHAVIOR_DEF = tpls.BEHAVIOR_DEF_TPL % (", ".join(names), ", ".join(names))
    f.write(BEHAVIOR_DEF + "\n")

write_behavior_h('behavior.h')

write_builtin_c("_builtin.c")