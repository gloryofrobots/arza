from obin.objects.space import newmodule
from obin.objects import api
from obin.runtime.exception import ObinImportError
from obin.utils.fs import file_get_contents, is_file, join_and_normalise_path
import os



def compile_module(process, name, txt):
    from obin.compile.compiler import compile
    code = compile(txt)
    module = newmodule(name, code)
    return module


def import_module(process, name):
    try:
        return process.get_module(name)
    except KeyError:
        return load_module(process, name)


def load_module(process, name):
    raw = api.to_native_unicode(name)
    path = raw.replace(u".", os.sep)
    path = path + u".obn"
    script = None
    for directory in process.path:
        filename = join_and_normalise_path(directory, path)
        if is_file(filename):
            script = file_get_contents(filename)
            break

        if not script:
            raise ObinImportError(unicode(name))

    return create_module(process, name, script)


def create_module(process, name, script):
    module = compile_module(process, name, script)
    process.run_module_force(module, process.builtins)
    process.add_module(name, module)
    return module
