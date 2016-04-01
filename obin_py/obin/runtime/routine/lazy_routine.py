__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.types import api, space, plist
from obin.runtime import error

# TODO IT
class LazyRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, stack, function, args):
        BaseRoutine.__init__(self, stack, args)
        self.constructor = function
        self._args = args

    def _info(self):
        return self.constructor.name

    def _on_resume(self, value):
        self.result = value

    def _execute(self, process):
        if self.result is not None:
            self.complete(process, self.result)
        else:
            api.call(process, self.constructor, self._args)

    def _on_complete(self, process):
        # CODE HERE
        pass
