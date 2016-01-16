__author__ = 'gloryofrobots'
from obin.runtime.routine.base_routine import BaseRoutine
from obin.types import api

class NativeRoutine(BaseRoutine):
    # _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, stack, name, function, args, arity):
        BaseRoutine.__init__(self, stack)
        from obin.types.space import issymbol
        assert issymbol(name)
        self._name_ = name
        self.native_func = function
        self.arity = arity
        self.count_args = api.n_length(args)
        self._args = args

    # redefine resume because we can call bytecode routine from native and after it resumes as we must complete
    def _on_resume(self, value):
        self.result = value

    def _on_complete(self, process):
        pass

    def name(self):
        return api.to_native_string(self._name_)

    def args(self):
        return self._args

    def get_arg(self, index):
        return api.at_index(self._args, index)

    def _execute(self, process):
        if self.result is not None:
            self.complete(process, self.result)
        else:
            self.suspend()
            self.native_func(process, self)

