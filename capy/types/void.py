from root import W_UniqueType

class W_Void(W_UniqueType):
    def _to_string_(self):
        return 'void'

    def _to_repr_(self):
        return self._to_string_()

class W_Nil(W_UniqueType):
    def _to_string_(self):
        return 'Nil'

    def _to_repr_(self):
        return self._to_string_()
