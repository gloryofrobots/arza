BEGIN = "self."
LEN = len(BEGIN)

def transform_line(line, index, varname, funcargs):
    start_search_index = index + LEN
    try:
        property_check = line.index("property_", index)
        # print "p_check", start_search_index, property_check
        if property_check == start_search_index:
            nline = line.replace(BEGIN, varname + ".", 1)
            return nline, index
    except:
        pass
        # print "not property, working"

    nline = line.replace(BEGIN, "", 1)
    nline = nline.replace("(", "(" + funcargs + ",", 1)
    return nline, index


def transform(string, varname, funcargs):
    lines = string.split("\n")
    result = []
    for line in lines:
        index = 0
        newline = line
        while True:
            try:
                index = newline.index(BEGIN, index)
                newline, index = transform_line(newline, index, varname, funcargs)
            except:
                break
        result.append(newline)
    return "\n".join(result)



T = "self._compile_modify_assignment_primitive(code, node, internals.ADD)"
T= "scope = self.current_scope()"
T = "for scope in reversed(self.property_scopes):"


print transform(T, "compiler", "process, compiler")