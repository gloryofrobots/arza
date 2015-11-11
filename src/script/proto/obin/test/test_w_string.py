from obin.objects.object import W_String


def test_string_to_number():
    assert W_String(u'').ToNumber() == 0
    assert W_String(u' ').ToNumber() == 0
    assert W_String(u'\t').ToNumber() == 0
    assert W_String(u'\n').ToNumber() == 0
    assert W_String(u'\r').ToNumber() == 0
    assert W_String(u'\r\n').ToNumber() == 0


def test_isspace():
    from obin.builtins.global_builtins import _strip
    assert _strip(u' ') == u''
    assert _strip(u'    ') == u''
    assert _strip(u'  \t\t\r\n  ') == u''
    assert _strip(u'  \t\ts\r\n  ') == u's'
