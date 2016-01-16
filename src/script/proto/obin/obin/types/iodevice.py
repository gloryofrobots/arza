__author__ = 'gloryofrobots'
from obin.types.root import W_Any
from obin.types import api

class IoDevice(W_Any):
    def __init__(self, fd):
        self.file = fd

    def write_s(self, data):
        self.file.write(data)

    def write_u(self, data):
        self.file.write(data)

    def write(self, obj):
        ustr = api.to_native_unicode(obj)
        self.write_u(ustr)

    def writer(self):
        return Writer(self)

class Writer:
    def __init__(self, device):
        self.device = device

    def nl(self):
        self.device.write_s("\n")
        return self

    def tab4(self):
        self.device.write_s("    ")
        return self

    def write_s(self, s):
        self.device.write_s(s)
        return self

    def write(self, obj):
        self.device.write(obj)
        return self