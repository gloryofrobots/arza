__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.types import api, space, plist
from obin.runtime import error

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
        if not space.islist(self.result):
            return error.throw_2(error.Errors.ORIGINATE,
                                 space.newstring(u"list[source, ...traits] expected"),
                                 self.result)

        source = plist.head(self.result)
        traits = plist.fmap(api.totrait, plist.tail(self.result))
        self.result = space.newentity(process, source, traits)
        # print "Origin on complete", self.result
