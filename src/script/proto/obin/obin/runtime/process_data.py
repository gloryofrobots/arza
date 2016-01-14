class Modules:
    def __init__(self, path):
        assert isinstance(path, list)
        self.modules = {}
        self.path = path

    def add_path(self, path):
        assert isinstance(path, str)
        self.path.append(path)

    def add_module(self, name, module):
        self.modules[name] = module

    def get_module(self, name):
        return self.modules[name]


class ProcessData:
    def __init__(self, modules, std, builtins):
        self.modules = modules
        self.std_objects = std
        self.builtins = builtins


def create(libdirs, stdlib, builtins):
    modules = Modules(libdirs)
    return ProcessData(modules, stdlib, builtins)
