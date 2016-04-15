from obin.runtime import error
from obin.types import api, space

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

def cat_both_ends(string):
    if len(string) < 2:
        return None
    return string[1:len(string) - 1]

def unquote_w(w):
    return space.newstring_s(unquote_s(api.to_s(w)))

def unquote_s(string):
    s = string
    if s.startswith('"""'):
        assert s.endswith('"""')
        s = s[:-3]
        s = s[3:]
    elif s.startswith('"'):
        assert s.endswith('"')
        s = s[:-1]
        s = s[1:]
    elif s.startswith("'"):
        assert s.endswith("'")
        s = s[:-1]
        s = s[1:]

    return s
