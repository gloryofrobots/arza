from obin.objects.object import W_Array
from obin.objects.property import DataProperty
from obin.objects.object_space import _w


def test_array_put_change_index():
    a = W_Array()
    a.put(u'0', 42)
    assert a.get(u'0') == 42
    a.put(u'0', 43)
    assert a.get(u'0') == 43


def test_array_get():
    a = W_Array()
    a._set_prop(u'23', DataProperty(42, True, True, True))
    assert a.get(u'23') == 42


def test_array_iprop():
    d = DataProperty(42, True, True, True)
    a = W_Array()
    a._set_iprop(23, d)
    assert a._get_iprop(23) is d
    assert a._get_prop(u'23') is d
    assert a.get(u'23') == 42


def test_array_w_get():
    d = DataProperty(42, True, True, True)
    a = W_Array()
    a._set_iprop(23, d)
    assert a.w_get(_w(23)) == 42
    assert a.w_get(_w(u'23')) == 42


def test_array_put():
    a = W_Array()
    a.put(u'23', 42)
    assert a.get(u'23') == 42
    assert a.w_get(_w(u'23')) == 42


def test_array_w_put():
    a = W_Array()
    a.w_put(_w(23), 42)
    assert a.get(u'23') == 42
    assert a.w_get(_w(23)) == 42
    assert a.w_get(_w(u'23')) == 42
