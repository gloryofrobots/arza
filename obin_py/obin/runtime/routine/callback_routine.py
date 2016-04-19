__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.types import api, space, plist
from obin.runtime import error

class CallbackRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, stack, callback, function, args):
        BaseRoutine.__init__(self, stack)
        self.function = function
        self.args = args
        self.callback = callback

    def _info(self):
        return self.function.name

    # HERE WE GOT RESULT OF FUNCTION CALL
    def _on_resume(self, process, value):
        self.result = self.callback(process, value)

    def _execute(self, process):
        # ALREADY RESUMED WITH RESULT
        if self.result is not None:
            self.complete(process, self.result)
        else:
            api.call(process, self.function, self.args)

    def _on_complete(self, process):
        pass
