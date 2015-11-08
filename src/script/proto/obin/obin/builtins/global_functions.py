# -*- coding: utf-8 -*-

from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from rpython.rlib.rfloat import NAN, INFINITY, isnan, isinf
from obin.builtins import get_arg
from rpython.rlib.unicodedata import unicodedb
from obin.objects import api


def setup(global_object):
    from rpython.rlib.objectmodel import we_are_translated
    from obin.builtins.number import w_NAN
    from obin.builtins.number import w_POSITIVE_INFINITY
    from obin.objects.object_space import newundefined

    # 15.1.1.1
    api.put_property(global_object, u'NaN', w_NAN)

    # 15.1.1.2
    api.put_property(global_object, u'Infinity', w_POSITIVE_INFINITY)

    # 15.1.2.1
    api.put_native_function(global_object, u'eval', _eval, params=[u'x'])

    # 15.1.2.2
    api.put_native_function(global_object, u'parseInt', parse_int, params=[u'string', u'radix'])

    # 15.1.2.3
    # TODO
    api.put_native_function(global_object, u'parseFloat', parse_float, params=[u'string'])

    # 15.1.2.4
    api.put_native_function(global_object, u'isNaN', is_nan, params=[u'number'])

    # 15.1.2.5
    api.put_native_function(global_object, u'isFinite', is_finite, params=[u'number'])

    api.put_native_function(global_object, u'alert', alert)

    api.put_native_function(global_object, u'print', _print)
    api.put_native_function(global_object, u'id', _id)
    api.put_native_function(global_object, u'now', now)

    api.put_native_function(global_object, u'escape', escape, params=[u'string'])

    api.put_native_function(global_object, u'unescape', unescape, params=[u'string'])

    api.put_native_function(global_object, u'version', version)

    ## debugging
    if not we_are_translated():
        api.put_native_function(global_object, u'pypy_repr', pypy_repr)
        api.put_native_function(global_object, u'inspect', inspect)


# 15.1.2.4
@complete_native_routine
def is_nan(ctx, routine):
    args = routine.args()
    if len(args) < 1:
        return True
    return isnan(args[0].ToNumber())


# 15.1.2.5
@complete_native_routine
def is_finite(ctx, routine):
    args = routine.args()
    if len(args) < 1:
        return True
    n = args[0].ToNumber()
    if isinf(n) or isnan(n):
        return False
    else:
        return True


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
def parse_int(ctx, routine):
    args = routine.args()
    string = get_arg(args, 0)
    radix = get_arg(args, 1)

    return _parse_int(string.to_string(), radix.ToInt32())

def now(self, args):
    print "W_DateConstructor Call"
    import time
    from obin.objects.object_space import _w
    value = _w(int(time.time() * 1000))

    from obin.objects.object_space import object_space
    obj = object_space.new_date(value)
    return obj

@complete_native_routine
def _id(ctx, routine):
    args = routine.args()
    element = get_arg(args, 0)
    return str(hex(id(element)))

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
def parse_float(ctx, routine):
    args = routine.args()
    from obin.runistr import encode_unicode_utf8
    from obin.constants import num_lit_rexp

    string = get_arg(args, 0)
    input_string = string.to_string()
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
def alert(ctx, routine):
    _print(ctx, routine)

def dummy(ctx, routine):
    pass

@complete_native_routine
def _print(ctx, routine):
    args = routine.args()
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
def escape(ctx, routine):
    args = routine.args()
    CHARARCERS = u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./'
    string = get_arg(args, 0)
    r1 = string.to_string()
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
def unescape(ctx, routine):
    args = routine.args()
    string = get_arg(args, 0)
    r1 = string.to_string()
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


@complete_native_routine
def pypy_repr(ctx, routine):
    args = routine.args()
    o = args[0]
    return str(o)


@complete_native_routine
def inspect(ctx, routine):
    pass


def _make_version_string():
    return ""

_version_string = _make_version_string()


@complete_native_routine
def version(ctx, routine):
    return _version_string

from obin.runtime.machine import run_routine_for_result
from obin.objects.object_space import _w

# 15.1.2.1
def _eval(ctx, routine):
    from obin.objects.object_space import isstring
    from obin.runtime.routine import BytecodeRoutine
    from obin.runtime.execution_context import EvalExecutionContext

    args = ctx.argv()
    x = get_arg(args, 0)

    assert isstring(x)

    src = x.value()
    from obin.compile.compiler import compile as cl
    code = cl(src)
    f = BytecodeRoutine(code)
    ctx = EvalExecutionContext(f)
    f.set_context(ctx)
    routine.call_routine(f)


def js_load(ctx):
    from obin.runtime.interpreter import load_file
    from obin.compile.code import ast_to_bytecode
    from obin.runtime.routine import BytecodeRoutine
    from obin.runtime.execution_context import EvalExecutionContext

    args = ctx.argv()
    f = get_arg(args, 0)
    filename = f.to_string()

    ast = load_file(filename)
    symbol_map = ast.symbol_map
    code = ast_to_bytecode(ast, symbol_map)

    f = BytecodeRoutine(code)
    calling_context = ctx._calling_context_

    ctx = EvalExecutionContext(f, calling_context=calling_context)
    result = run_routine_for_result(f, ctx)
    return _w(result)

