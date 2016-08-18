__author__ = 'gloryofrobots'
from lalan.types.root import W_Root
from lalan.types import api

class W_IODevice(W_Root):
    def __init__(self, fd):
        self.file = fd

    def write(self, obj):
        ustr = api.to_u(obj)
        self.file.write(ustr)

    def _to_string_(self):
        return "<iodevice>"

    def _to_repr_(self):
        return self._to_string_()


