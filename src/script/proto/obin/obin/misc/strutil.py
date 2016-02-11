from obin.runtime import error

def get_line(string, line_no):
    index = -1
    for _ in range(line_no - 1):
        index = string.index('\n', index + 1)

    try:
        last_index = string.index('\n', index + 1)
        result = string[index + 1:last_index]
    except ValueError:
        result = string[index + 1:]

    result = result.lstrip()
    return unicode(result)


def get_line_for_position(string, pos):
    try:
        index = string.index('\n', pos + 1)
        result = string[pos: index]
    except:
        result = string[pos:]
    return unicode(result)


def is_quoted_string(string):
    if string.startswith('"') and string.endswith('"'):
        return True
    if string.startswith("'") and string.endswith("'"):
        return True
    return False


def string_to_int(string):
    return int(string)


def string_unquote(string):
    s = string
    if s.startswith('"'):
        assert s.endswith('"')
    else:
        assert s.startswith("'")
        assert s.endswith("'")
    s = s[:-1]
    s = s[1:]

    return s
