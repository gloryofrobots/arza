__author__ = 'gloryofrobots'
from obin.runtime.routine.base import BaseRoutine

class NativeRoutine(BaseRoutine):
    _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, name, function, args, arity):
        super(NativeRoutine, self).__init__()
        from obin.objects.object_space import isstring
        assert isstring(name)
        self._name_ = name
        self._function_ = function
        self.arity = arity
        self.count_args = args.length()
        self._args = args

    # redefine resume because we can call bytecode routine from native and after it resumes as we must complete
    resume = BaseRoutine.complete

    def name(self):
        return self._name_.value()

    def get_arg(self, index):
        return self._args.at(index)

    def _execute(self):
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        self.suspend()
        self._function_(self)

    def _on_complete(self):
        pass
        # self.ctx.stack_append(self.result)

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { [native code] }' % (name,)
        else:
            return u'function () { [native code] }'
