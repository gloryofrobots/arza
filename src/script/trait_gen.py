TRAITS = [
        "Any", 
        "Boolean", 

        "True", 
        "False", 
        "Nil", 
        "Char", 

        "Number", 
        "Integer", 
        "Float", 
        "Symbol", 
        "String", 

        "List", 
        "Vector", 
        "Tuple", 
        "Map", 

        "Callable", 
        "Function", 
        "Fiber", 
        "Generic", 
        "Primitive", 

        "Environment", 
        "TVar",
        "Module", 
        "Behavior", 
        "Trait",
        "Collection",
        "Seq",
        "Indexed", 
        ]

print "#####################################################"
print "#####################################################"

def print_declarations():
    for T in TRAITS:
        S = '        self.%s = newtrait(symbols.symbol(u"%s"))' % (T, T)
        print S
print_declarations()

print "#####################################################"
print "#####################################################"

def print_builtin_puts():
    for T in TRAITS:
        S = "    api.put(module, traits.%s.name, traits.%s)" % (T, T)
        print S

print_builtin_puts()
        