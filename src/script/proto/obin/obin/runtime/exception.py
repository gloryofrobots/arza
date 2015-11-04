class ObinException(Exception):
    message = u'Exception'

    def __init__(self, message=None):
        if message is not None:
            assert isinstance(message, unicode)
            self.message = message

    def _msg(self):
        return self.message

    def msg(self):
        from obin.objects.object_space import _w
        return _w(self._msg())


class ObinThrowException(ObinException):
    def __init__(self, value):
        from obin.objects.object import W_Root
        assert isinstance(value, W_Root)
        self.value = value

    def _msg(self):
        s = self.value.to_string()
        return s


class ObinTypeError(ObinException):
    def __init__(self, value):
        from obin.utils import tb
        tb()
        # assert isinstance(value, unicode)
        self.value = value

    def _msg(self):
        return u'TypeError : ' + self.value  # % (self.value, )


class ObinReferenceError(ObinException):
    def __init__(self, identifier):
        self.identifier = identifier

    def _msg(self):
        return u'ReferenceError: ' + self.identifier + u' is not defined'


class ObinRangeError(ObinException):
    def __init__(self, value=None):
        self.value = value

    def _msg(self):
        return u'RangeError: %s' % (self.value,)


class ObinKeyError(ObinRangeError):
    def __init__(self, value=None):
        self.value = value

    def _msg(self):
        return u'KeyError: %s' % (self.value,)


class ObinSyntaxError(ObinException):
    def __init__(self, msg=u'', src=u'', line=0, column=0):
        self.error_msg = msg
        self.src = src
        self.line = line
        self.column = column

    def _msg(self):
        # error_src = self.src #self.src.encode('unicode_escape')
        if self.error_msg:
            return u'SyntaxError: "%s" in "%s" at line:%d, column:%d'  # %(self.error_msg, error_src, self.line, self.column)
        else:
            return u'SyntaxError: in "%s" at line:%d, column:%d'  # %(error_src, self.line, self.column)
