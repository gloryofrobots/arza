class Pattern(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return "<%s %s>" % (str(self.type), str(self.value))


def list_pattern(patterns):
    return Pattern("LIST", patterns)


def table_pattern(patterns):
    return Pattern("TABLE", patterns)


def value_pattern(val):
    return Pattern("VAL", val)


def var_pattern(val):
    return Pattern("VAR", val)


def constant_pattern(val):
    return Pattern("CONST", val)


def pair_pattern(p1, p2):
    return Pattern("PAIR", (p1, p2))


def wildcard_pattern():
    return Pattern("WILD", None)


def is_wildcard_pattern(pattern):
    return pattern.type == "WILD"


def is_constant_pattern(pattern):
    return pattern.type == "CONST"


def is_value_pattern(pattern):
    return pattern.type == "VAL"


def is_var_pattern(pattern):
    return pattern.type == "VAR"


def is_list_pattern(pattern):
    return pattern.type == "LIST"


def is_table_pattern(pattern):
    return pattern.type == "TABLE"


def is_pair_pattern(pattern):
    return pattern.type == "PAIR"


def pattern_value(pattern):
    return pattern.value


def list_pattern_length(p):
    return len(p.value)

