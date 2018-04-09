__author__ = 'gloryofrobots'
from capy.types.root import W_Root
from capy.types import api
import sys

class W_IODevice(W_Root):
    def __init__(self, fd):
        self.file = fd

    def write(self, obj):
        ustr = api.to_u(obj)
        self.file.write(ustr)
        self.file.flush()

    def _type_(self, process):
        return process.classes.File

    def _to_string_(self):
        return "<iodevice>"

    def _to_repr_(self):
        return self._to_string_()


