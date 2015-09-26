
class EnvironmentRecord(object):
    def has_binding(self, identifier):
        return False

    def create_binding(self, identifier):
        raise NotImplementedError

    def set_binding(self, identifier, value):
        raise NotImplementedError

    def get_binding_value(self, identifier):
        raise NotImplementedError


class DeclarativeEnvironmentRecord(EnvironmentRecord):
    _immutable_fields_ = ['_binding_slots_', '_binding_resize_']

    def __init__(self, size):
        from obin.objects.datastructs import Slots
        EnvironmentRecord.__init__(self)
        self.bindings = Slots(size)

    # 10.2.1.1.1
    def has_binding(self, identifier):
        return self.bindings.contains(identifier)

    def _get_binding(self, name):
        return self.bindings.get(name)

    def _add_binding(self, name, value):
        self.bindings.add(name, value)

    def _set_binding(self, name, value):
        self.bindings.set(name, value)

    def _del_binding(self, name):
        self.bindings.delete(name)

    # 10.2.1.1.2
    def create_binding(self, identifier):
        from obin.objects.object_space import newundefined
        assert identifier is not None and isinstance(identifier, unicode)
        assert not self.has_binding(identifier)
        self._add_binding(identifier, newundefined())

    # 10.2.1.1.3
    def set_binding(self, identifier, value):
        assert identifier is not None and isinstance(identifier, unicode)
        assert self.has_binding(identifier)
        self._set_binding(identifier, value)

    # 10.2.1.1.4
    def get_binding_value(self, identifier):
        assert identifier is not None and isinstance(identifier, unicode)
        if not self.has_binding(identifier):
                from obin.runtime.exception import JsReferenceError
                raise JsReferenceError(identifier)

        return self._get_binding(identifier)


class ObjectEnvironmentRecord(EnvironmentRecord):
    _immutable_fields_ = ['binding_object']

    provide_this = False

    def __init__(self, obj, provide_this=False):
        self.binding_object = obj
        if provide_this is True:
            self.provide_this = True

    # 10.2.1.2.1
    def has_binding(self, n):
        assert n is not None and isinstance(n, unicode)
        bindings = self.binding_object
        return bindings.has_property(n)

    # 10.2.1.2.2
    def create_binding(self, n):
        from obin.objects.object_space import newundefined
        assert n is not None and isinstance(n, unicode)
        bindings = self.binding_object
        assert bindings.has_property(n) is False

        bindings.put(n, newundefined())

    # 10.2.1.2.3
    def set_binding(self, n, v):
        assert n is not None and isinstance(n, unicode)
        bindings = self.binding_object
        bindings.put(n, v)

    # 10.2.1.2.4
    def get_binding_value(self, n):
        assert n is not None and isinstance(n, unicode)
        bindings = self.binding_object
        value = bindings.has_property(n)
        if value is False:
            from obin.runtime.exception import JsReferenceError
            raise JsReferenceError(self.__class__)

        return bindings.get(n)

    # 10.2.1.2.5
    def delete_binding(self, n):
        assert n is not None and isinstance(n, unicode)
        bindings = self.binding_object
        return bindings.delete(n, False)


class GlobalEnvironmentRecord(ObjectEnvironmentRecord):
    pass
