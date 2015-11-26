# -*- coding: utf-8 -*-

from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from rpython.rlib.rfloat import NAN, INFINITY, isnan, isinf
from rpython.rlib.unicodedata import unicodedb
from obin.objects import api


def setup(obj):
    from rpython.rlib.objectmodel import we_are_translated
    from obin.builtins.number_builtins import w_NAN
    from obin.builtins.number_builtins import w_POSITIVE_INFINITY
    from obin.objects.object_space import object_space

    ### Traits
    traits = object_space.traits
    api.put_property(obj, u'True', traits.True)
    api.put_property(obj, u'False', traits.False)
    api.put_property(obj, u'Boolean', traits.Boolean)
    api.put_property(obj, u'Nil', traits.Nil)
    api.put_property(obj, u'Undefined', traits.Undefined)
    api.put_property(obj, u'Char', traits.Char)
    api.put_property(obj, u'Number', traits.Number)
    api.put_property(obj, u'Integer', traits.Integer)
    api.put_property(obj, u'Float', traits.Float)
    api.put_property(obj, u'Symbol', traits.Symbol)
    api.put_property(obj, u'String', traits.String)
    api.put_property(obj, u'Array', traits.Array)
    api.put_property(obj, u'Vector', traits.Vector)
    api.put_property(obj, u'Tuple', traits.Tuple)
    api.put_property(obj, u'Object', traits.Object)
    api.put_property(obj, u'Function', traits.Function)


    # 15.1.1.1
    api.put_property(obj, u'NaN', w_NAN)

    # 15.1.1.2
    api.put_property(obj, u'Infinity', w_POSITIVE_INFINITY)

    # 15.1.2.1
    api.put_native_function(obj, u'eval', _eval, 1)
    api.put_native_function(obj, u'print', _print, -1)
    api.put_native_function(obj, u'id', _id, 1)
    api.put_native_function(obj, u'escape', escape, 1)
    api.put_native_function(obj, u'unescape', unescape, 1)

    api.put_native_function(obj, u'version', version, 0)
    api.put_native_function(obj, u'coroutine', coroutine, 1)
    api.put_native_function(obj, u'range', _range, 2)

    ## debugging
    # if not we_are_translated():
    #     api.put_native_function(obj, u'pypy_repr', pypy_repr)
    #     api.put_native_function(obj, u'inspect', inspect)


def _isspace(uchar):
    return unicodedb.isspace(ord(uchar))

def _strip(unistr, left=True, right=True):
    lpos = 0
    rpos = len(unistr)

    if left:
        while lpos < rpos and _isspace(unistr[lpos]):
            lpos += 1

    if right:
        while rpos > lpos and _isspace(unistr[rpos - 1]):
            rpos -= 1

    assert rpos >= 0
    result = unistr[lpos:rpos]
    return result


def _lstrip(unistr):
    return _strip(unistr, right=False)


def _string_match_chars(string, chars):
    for char in string:
        c = unichr(unicodedb.tolower(ord(char)))
        if c not in chars:
            return False
    return True

# 15.1.2.2
@complete_native_routine
def parse_int(routine):
    string = routine.get_arg(0)
    radix = routine.get_arg(1)

    return _parse_int(string.to_string(), radix.value())

def now(self, args):
    print "W_DateConstructor Call"
    import time
    from obin.objects.object_space import _w
    value = _w(int(time.time() * 1000))

    from obin.objects.object_space import object_space
    obj = object_space.new_date(value)
    return obj

@complete_native_routine
def _id(routine):
    this = routine.get_arg(0)
    return str(hex(id(this)))

def _parse_int(string, radix):
    assert isinstance(string, unicode)
    NUMERALS = u'0123456789abcdefghijklmnopqrstuvwxyz'
    input_string = string
    s = _strip(input_string)
    sign = 1

    if s.startswith(u'-'):
        sign = -1
    if s.startswith(u'-') or s.startswith(u'+'):
        s = s[1:]

    r = radix
    strip_prefix = True

    if r != 0:
        if r < 2 or r > 36:
            return NAN
        if r != 16:
            strip_prefix = False
    else:
        r = 10

    if strip_prefix:
        if len(s) >= 2 and (s.startswith(u'0x') or s.startswith(u'0X')):
            s = s[2:]
            r = 16
        # TODO this is not specified in ecma 5 but tests expect it and it's implemented in v8!
        elif len(s) > 1 and s.startswith(u'0'):
            r = 8

    numerals = NUMERALS[:r]

    z = []
    for char in s:
        uni_ord = unicodedb.tolower(ord(char))
        if uni_ord > 128:
            break
        c = chr(uni_ord)
        if c not in numerals:
            break
        z.append(c)

    if not z:
        return NAN

    num_str = ''.join(z)

    try:
        number = int(num_str, r)
        try:
            from rpython.rlib.rarithmetic import ovfcheck_float_to_int
            ovfcheck_float_to_int(number)
        except OverflowError:
            number = float(number)
        return sign * number
    except OverflowError:
        return INFINITY
    except ValueError:
        pass

    return NAN


# 15.1.2.3
@complete_native_routine
def parse_float(routine):
    from obin.runistr import encode_unicode_utf8
    from obin.constants import num_lit_rexp

    string = routine.get_arg(0)
    input_string = string.value()
    trimmed_string = _strip(input_string)
    str_trimmed_string = encode_unicode_utf8(trimmed_string)

    match_data = num_lit_rexp.match(str_trimmed_string)
    if match_data is not None:
        number_string = match_data.group()
    else:
        number_string = ''

    if number_string == 'Infinity' or number_string == '+Infinity':
        return INFINITY
    elif number_string == '-Infinity':
        return -INFINITY

    try:
        number = float(number_string)
        return number
    except ValueError:
        pass

    return NAN



@complete_native_routine
def alert(routine):
    _print(routine)

@complete_native_routine
def _print(routine):
    args = routine._args.values()
    if len(args) == 0:
        return

    from rpython.rlib.rstring import UnicodeBuilder
    from obin.runistr import encode_unicode_utf8

    builder = UnicodeBuilder()
    for arg in args[:-1]:
        builder.append(api.tostring(arg).value())
        builder.append(u',')

    builder.append(api.tostring(args[-1]).value())

    u_print_str = builder.build()
    print_str = encode_unicode_utf8(u_print_str)
    print(print_str)


def hexing(i, length):
    h = unicode(hex(i).upper())
    assert h.startswith('0X')
    h = h[2:]

    while(len(h) < length):
        h = u'0' + h

    return h


# B.2.1
@complete_native_routine
def escape(routine):
    CHARARCERS = u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./'
    string = routine.get_arg(0)
    r1 = string.value()
    r2 = len(r1)
    r = u''
    k = 0

    while k != r2:
        c = r1[k]
        r6 = ord(c)
        if c in CHARARCERS:
            # step 13
            s = c
        elif r6 < 256:
            # step 11
            s = u'%' + hexing(r6, 2)
        else:
            s = u'%u' + hexing(r6, 4)
        r += s
        k += 1

    return r


# B.2.2
@complete_native_routine
def unescape(routine):
    string = routine.get_arg(0)
    r1 = string.value()
    r2 = len(r1)

    r = u''
    k = 0
    hexchars = u'0123456789abcdef'

    while k != r2:
        c = r1[k]
        if c == u'%':
            # 8. 9. 10.
            if (k > r2 - 6) or (r1[k + 1] != u'u') or (not len(r1) == 6 and _string_match_chars(r1[k + 2:k + 6], hexchars)):
                # got step 14
                if k > r2 - 3:  # 14.
                    pass  # goto step 18
                else:
                    if not _string_match_chars(r1[k + 1:k + 3], hexchars):  # 15.
                        pass  # goto step 18
                    else:
                        # 16
                        hex_numeral = u'00' + r1[k + 1:k + 3]
                        number = int(str(hex_numeral), 16)
                        c = unichr(number)
                        #17
                        k += 2
            else:
                # 11.
                hex_numeral = r1[k + 2:k + 6]
                number = int(str(hex_numeral), 16)
                c = unichr(number)

                # 12.
                k += 5
        # step 18
        r += c
        k += 1

    return r


def _make_version_string():
    return ""

_version_string = _make_version_string()


@complete_native_routine
def version(routine):
    return _version_string

def _eval(routine):
    from obin.objects.object_space import isstring
    from obin.runtime.routine import create_eval_routine

    x = routine.get_arg(0)

    assert isstring(x)

    src = x.value()
    from obin.compile.compiler import compile as cl
    code = cl(src)
    f = create_eval_routine(code)
    routine.call_routine(f)

@complete_native_routine
def coroutine(routine):
    from obin.objects.object_space import newcoroutine, isfunction
    fn = routine.get_arg(0)
    assert isfunction(fn)
    return newcoroutine(fn)

@complete_native_routine
def _range(routine):
    from obin.objects.object_space import newvector, newint
    start = routine.get_arg(0)
    end = routine.get_arg(1)
    items = [newint(i) for i in xrange(start.value(), end.value())]
    return newvector(items)
