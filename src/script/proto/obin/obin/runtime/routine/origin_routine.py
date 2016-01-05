__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.objects import api

class OriginRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, function, args):
        BaseRoutine.__init__(self)
        self.constructor = function
        self._args = args

    def _on_resume(self, value):
        self.result = value

    def _execute(self, process):
        if self.result is not None:
            self.complete(self.result)
        else:
            api.call(process, self.constructor, self._args)

    def _on_complete(self):
        print "Origin on complete", self.result
