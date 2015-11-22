from obin.objects.object_space import newvector

class Slots(object):
    def __init__(self):
        self.property_values = None
        self.property_bindings = None
        self.index = 0

    def to_dict(self):
        m = {}
        for n, v in self.property_bindings.items():
            m[n] = self.property_values.at(v)

        return m

    def __str__(self):
        return str(self.to_dict())
        pass

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        from copy import copy
        clone = Slots()
        clone.property_values = copy(self.property_values)
        clone.property_bindings = copy(self.property_bindings)
        clone.index = self.index
        return clone

    def contains(self, name):
        return name in self.property_bindings

    def length(self):
        return self.property_values.length()

    def keys(self):
        return self.property_bindings.keys()

    def get(self, name):
        idx = self.get_index(name)
        if idx is None:
            return

        return self.get_by_index(idx)

    def get_index(self, name):
        try:
            idx = self.property_bindings[name]
        except KeyError:
            return None
        return idx

    def set_by_index(self, idx, value):
        self.property_values.set(idx, value)

    def get_by_index(self, idx):
        return self.property_values.at(idx)

    def set(self, name, value):
        idx = self.get_index(name)
        self.set_by_index(idx, value)

    def add(self, name, value):
        idx = self.get_index(name)
        if idx is None:
            idx = self.index
            self.property_bindings[name] = idx
            self.index += 1

        if idx >= self.property_values.length():
            values = self.property_values.values()
            values = values + ([None] * (1 + idx - len(values)))
            self.property_values.set_values(values)

        self.set_by_index(idx, value)
        return idx

    def delete(self, name):
        idx = self.get_index(name)
        if idx is None:
            return

        assert idx >= 0
        values = self.property_values.values()
        values = values[:idx] + values[idx + 1:]
        self.property_values.set_values(values)

        del self.property_bindings[name]


def newslots(values, bindings, index):
    slots = Slots()
    slots.property_bindings = bindings
    slots.property_values = values
    slots.index = index
    return slots

def newslots_with_size(size):
    return newslots(newvector([None] * size), {}, 0)

def newslots_empty():
    return newslots(newvector([]), {}, 0)

def newslots_with_values_from_slots(values, protoslots):
    from copy import copy
    l = protoslots.length()
    size = values.length()
    diff = l - size
    assert diff >= 0
    if diff > 0:
        values.append_value_multiple_times(None, diff)

    bindings = copy(protoslots.property_bindings)
    index = protoslots.index
    return newslots(values, bindings, index)
