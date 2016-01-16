__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.types import api

class OriginRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, stack, function, args):
        BaseRoutine.__init__(self, stack)
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
        from obin.types.space import newentity, istuple, islist
        from obin.types.plist import head, tail, fmap
        if not islist(self.result):
            raise RuntimeError("Origin must return list[source, ...traits]")
        source = head(self.result)
        traits = fmap(api.totrait, tail(self.result))
        self.result = newentity(process, source, traits)
        # print "Origin on complete", self.result
