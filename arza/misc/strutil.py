from arza.misc.platform import (runicode, rarithmetic, rstring)
from arza.runtime import error
from arza.types import api, space


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


def decode_str_utf8(string):
    assert isinstance(string, str)
    result, consumed = runicode.str_decode_utf_8(string, len(string), "strict", True)
    return result


def encode_unicode_utf8(string):
    assert isinstance(string, unicode)
    result = runicode.unicode_encode_utf_8(string, len(string), None)
    return result


def decode_unicode_escape(string):
    assert isinstance(string, str)
    result, consumed = runicode.str_decode_unicode_escape(string, len(string), "strict", True)
    return result


def unescape_errorhandler(errors, encoding, msg, s, startingpos, endingpos):
    start = startingpos + 1
    assert start > 0
    assert endingpos > 0
    res = s[start:endingpos]
    return res, endingpos


# based on pypy.rlib.runicode str_decode_unicode_escape
def unicode_unescape(string):
    assert isinstance(string, unicode)
    s = string
    size = len(string)
    errorhandler = unescape_errorhandler
    errors = 'strict'

    if size == 0:
        return u''

    builder = rstring.UnicodeBuilder(size)
    pos = 0
    while pos < size:
        ch = s[pos]

        # Non-escape characters are interpreted as Unicode ordinals
        if ch != '\\':
            builder.append(unichr(ord(ch)))
            pos += 1
            continue

        # - Escapes
        pos += 1
        if pos >= size:
            raise RuntimeError(u"\\ at end of string")

        ch = s[pos]
        pos += 1
        # \x escapes
        if ch == '\n':
            pass
        elif ch == '\\':
            builder.append(u'\\')
        elif ch == '\'':
            builder.append(u'\'')
        elif ch == '\"':
            builder.append(u'\"')
        elif ch == 'b':
            builder.append(u'\b')
        elif ch == 'f':
            builder.append(u'\f')
        elif ch == 't':
            builder.append(u'\t')
        elif ch == 'n':
            builder.append(u'\n')
        elif ch == 'r':
            builder.append(u'\r')
        elif ch == 'v':
            builder.append(u'\v')
        elif ch == 'a':
            builder.append(u'\a')
        elif '0' <= ch <= '7':
            x = ord(ch) - ord('0')
            if pos < size:
                ch = s[pos]
                if '0' <= ch <= '7':
                    pos += 1
                    x = (x << 3) + ord(ch) - ord('0')
                    if pos < size:
                        ch = s[pos]
                        if '0' <= ch <= '7':
                            pos += 1
                            x = (x << 3) + ord(ch) - ord('0')
            builder.append(unichr(x))
        # hex escapes
        # \xXX
        elif ch == 'x':
            digits = 2
            message = "truncated \\xXX escape"
            pos = hexescape(builder, s, pos, digits, "unicodeescape", errorhandler, message, errors)

        # \uXXXX
        elif ch == 'u':
            digits = 4
            message = "truncated \\uXXXX escape"
            pos = hexescape(builder, s, pos, digits, "unicodeescape", errorhandler, message, errors)

        else:
            # builder.append(u'\\')
            builder.append(unichr(ord(ch)))

    return builder.build()


hexdigits = "0123456789ABCDEFabcdef"


def hexescape(builder, s, pos, digits, encoding, errorhandler, message, errors):
    chr = 0
    if pos + digits > len(s):
        message = "end of string in escape sequence"
        res, pos = errorhandler(errors, "unicodeescape", message, s, pos - 2, len(s))
        builder.append(res)
    else:
        try:
            chr = rarithmetic.r_uint(int(str(s[pos:pos + digits]), 16))
        except ValueError:
            endinpos = pos
            while s[endinpos] in hexdigits:
                endinpos += 1
            res, pos = errorhandler(errors, encoding, message, s, pos - 2, endinpos + 1)
            builder.append(res)
        else:
            # when we get here, chr is a 32-bit unicode character
            if chr <= runicode.MAXUNICODE:
                builder.append(runicode.UNICHR(chr))
                pos += digits

            elif chr <= 0x10ffff:
                chr -= 0x10000L
                builder.append(unichr(0xD800 + (chr >> 10)))
                builder.append(unichr(0xDC00 + (chr & 0x03FF)))
                pos += digits
            else:
                message = "illegal Unicode character"
                res, pos = errorhandler(errors, encoding, message, s, pos - 2, pos + digits)
                builder.append(res)
    return pos
