__author__ = 'gloryofrobots'
from obin.objects.space import _w
from rpython.rlib.rfloat import NAN, INFINITY, isnan, isinf
from rpython.rlib.unicodedata import unicodedb
from obin.objects import api

def setup(obj):
    from obin.objects.space import newgeneric

    from obin.builtins.number_builtins import w_NAN
    from obin.builtins.number_builtins import w_POSITIVE_INFINITY
    # 15.1.1.1

    api.put_string(obj, u'NaN', w_NAN)

    # 15.1.1.2
    api.put_string(obj, u'Infinity', w_POSITIVE_INFINITY)
    pass
