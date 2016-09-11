__author__ = 'gloryofrobots'
from lalan.runtime.routine.base_routine import BaseRoutine
from lalan.types import api, space, plist
from lalan.runtime import error


class CallbackRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, stack, on_result, on_complete, function, args):
        BaseRoutine.__init__(self, stack)
        self.function = function
        self.args = args
        self.on_result = on_result
        self.on_complete = on_complete
        self.result = None

    def _info(self):
        return self.function.name

    # HERE WE GOT RESULT OF FUNCTION CALL
    def _on_resume(self, process, value):
        if self.on_result:
            self.result = self.on_result(process, value)
        else:
            self.result = value

    def _execute(self, process):
        # ALREADY RESUMED WITH RESULT
        if self.result is not None:
            self.complete(process, self.result)
        else:
            api.call(process, self.function, self.args)

    def _on_complete(self, process):
        if self.on_complete:
            self.on_complete(process, self.result)
