I = "Integer"
N = "Number"
F = "Float"
A = "Any"


GENERICS = [
    ("Add", "+",
         [((I,I),"add_i_i"), ((F,F),"add_f_f"),
          ((N, N), "add_n_n")]),
    ("Sub", "-",
         [((I,I),"sub_i_i"), ((F,F),"sub_f_f"),
          ((N, N), "sub_n_n")]),
    ("Mul", "*",
         [((I,I),"mult_i_i"), ((F,F),"mult_f_f"),
          ((N, N), "mult_n_n")]),
    ("Div", "/",
         [((I,I),"div_i_i"), ((F,F),"div_f_f"),
          ((N, N), "div_n_n")]),
    ("Mod", "%",
         [((F,F),"mod_f_f"),
          ((N, N), "mod_n_n")]),
    ("UnaryPlus", "__unary_plus__",
         [((N,), "uplus_n")]),
    ("UnaryMinus", "__unary_minus__",
         [((I,),"uminus_i"), ((F,),"uminus_f"),
          ((N,), "uminus_n")]),
    ("Not", "not",
         [((A,),"not_w")]),
    ("Equal", "==",
         [((A,A),"eq_w")]),
    ("NotEqual", "!=",
         [((A,A),"noteq_w")]),
    ("Compare", "compare",None),
    ("In", "contains",
         [((A,A),"in_w")]),
    ("GreaterThen", ">",
         [((I,I),"compare_gt_i_i"), ((F,F),"compare_gt_f_f"),
          ((N, N), "compare_gt_n_n")]),
    ("GreaterEqual", ">=",
         [((I,I),"compare_ge_i_i"), ((F,F),"compare_ge_f_f"),
          ((N, N), "compare_ge_n_n")]),
    ("BitNot", "!",
         [((I,),"bitnot_i")]),
     ("BitOr", "^",
         [((I,I),"bitor_i_i")]),
     ("BitXor", "~",
         [((I,I),"bitxor_i_i")]),
     ("BitAnd", "&",
         [((I,I),"bitand_i_i")]),
     ("LeftShift", "<<",
         [((I,I),"lsh_i_i")]),
     ("RightShift", ">>",
         [((I,I),"rsh_i_i")]),
     ("UnsignedRightShift", ">>>",
         [((I,I),"ursh_i_i")]),

     ("Len", "len",
         [((A,),"len_w")]),
     ("Str", "str",
         [((A,),"str_w")]),
]
TPL_IMPL_BINARY = """
@complete_native_routine
def builtin_%s(process, routine):
    from obin.builtins.internals.operations import %s 
    arg1 = routine.get_arg(0)
    arg2 = routine.get_arg(1)
    return %s(process, arg1, arg2)
"""

TPL_IMPL_UNARY = """
@complete_native_routine
def builtin_%s(process, routine):
    from obin.builtins.internals.operations import %s 
    arg1 = routine.get_arg(0)
    return %s(process, arg1)
"""
print "#################### WRAPPERS #################################################"
def print_implementations():
    print "from obin.runtime.routine import complete_native_routine"
    for G in GENERICS:
        impls = G[2]
        if impls is None:
            continue
                
        for impl in impls:

            traits = impl[0]
            func = impl[1]
            if len(traits) == 1:
                tpl = TPL_IMPL_UNARY
            else:
                tpl = TPL_IMPL_BINARY
            S = tpl %(func, func, func)
            print S

print_implementations()

print "#####################################################"
print "#####################################################"

def print_declarations():
    for G in GENERICS:
        varname = G[0]
        funcname = G[1]
        S = "        self.%s = newgeneric(newstring(u\"%s\"))" % (varname, funcname)
        print S
print_declarations()

print "#####################################################"
print "#####################################################"

def print_builtin_puts():
    for G in GENERICS:
        varname = G[0]
        S = "    api.put(module, generics.%s.name, generics.%s)" % (varname, varname)
        print S

print_builtin_puts()

print "#####################################################"
print "#####################################################"

REIFY_TPL = """
    reify_single(process, generics.{{varname}},
                 newtuple([{% for trait in traits %}traits.{{trait}}, {% endfor %}]),
                 newprimitive(newstring(u"{{funcname}}"), wrappers.builtin_{{funcname}}, {{traits|length}}))
"""
    
def print_reify():
    from jinja2 import Template
    template = Template(REIFY_TPL)
    for G in GENERICS:
        impls = G[2]
        if impls is None:
            continue
        varname = G[0]
        

        for impl in impls:
            data = {"varname":varname, "funcname":impl[1], "traits":impl[0]}
            S = template.render(data)
            print S

print_reify()
 