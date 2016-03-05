def gen_cell_types(types):
    result = []
    for typeId, typeName in enumerate(types):
        varName = "__O%sTypeId__" %  typeName
        temp = "#define %s %d" % (varName, typeId)
        result.append(temp)
        temp = "#define OAny_is%s(any) OCell_isSameType(any, %s)" % (typeName, varName)
        result.append(temp)
    return result

types = gen_cell_types(["String", "Tuple", "Vector", "Table",
         "Bytecode", "Bytes", "FStream", "Iterator", "Array"])

for type in types:
    print type
