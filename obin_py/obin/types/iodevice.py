__author__ = 'gloryofrobots'
from obin.types.root import W_Root
from obin.types import api

class IoDevice(W_Root):
    def __init__(self, fd):
        self.file = fd

    def write(self, obj):
        ustr = api.to_u(obj)
        self.file.write(ustr)


