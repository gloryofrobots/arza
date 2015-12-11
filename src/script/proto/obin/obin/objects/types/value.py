from root import W_Root


class W_ValueType(W_Root):
    def value(self):
        raise NotImplementedError()


class W_Char(W_ValueType):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Char, self).__init__()
        self.__value = value

    def __str__(self):
        return '(%s)' % (unichr(self.__value),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return unichr(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.CharTraits


class W_Integer(W_ValueType):
    _immutable_fields_ = ['__value']

    def __init__(self, value):
        super(W_Integer, self).__init__()
        self.__value = value

        # def __str__(self):
        # return 'W_Integer(%d)' % (self.value(),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.IntegerTraits


class W_Float(W_ValueType):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Float, self).__init__()
        self.__value = value

    # def __str__(self):
    #     return 'W_Float(%s)' % (str(self.__value),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.FloatTraits


class NativeListIterator(W_ValueType):
    def __init__(self, source, length):
        self.index = 0
        self.source = source
        self.length = length

    def _next_(self):
        from obin.objects.object_space import newundefined
        if self.index >= self.length:
            return newundefined()

        el = self.source[self.index]
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.length)

    def _tobool_(self):
        if self.index >= self.length:
            return False
        return True


class W_String(W_ValueType):
    _type_ = 'String'
    _immutable_fields_ = ['value']

    def __init__(self, value):
        assert value is not None and isinstance(value, unicode)
        super(W_String, self).__init__()
        self.__items = value
        self.__length = len(self.__items)

    # def __str__(self):
    #     return u'W_String("%s")' % (self.__items)

    def __eq__(self, other):
        if isinstance(other, unicode):
            raise RuntimeError("It is not unicode")
        if isinstance(other, str):
            raise RuntimeError("It is not  str")
        if not isinstance(other, W_String):
            return False
        return self.value() == other.value()

    def __hash__(self):
        return self.value().__hash__()

    def isempty(self):
        return not bool(len(self.__items))

    def value(self):
        return self.__items

    def _tostring_(self):
        return str(self.__items)

    def _iterator_(self):
        return NativeListIterator(self.__items, self.__length)

    def _tobool_(self):
        return bool(self.__items)

    def _length_(self):
        return self.__length

    def _at_(self, index):
        from obin.objects.object_space import newundefined, newchar, isint
        from obin.runtime.exception import ObinKeyError
        assert isint(index)
        try:
            ch = self.__items[index.value()]
        except ObinKeyError:
            return newundefined()

        return newchar(ch)

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.StringTraits
