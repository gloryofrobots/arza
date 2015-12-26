from obin.objects.space import newmodule
from obin.objects import api
from obin.runtime.exception import ObinImportError
from obin.utils.fs import load_file_content, is_file, join_and_normalise_path
import os


def compile_module(process, name, txt):
    from obin.compile.compiler import compile
    code = compile(txt)
    module = newmodule(process, name, code)
    return module


def import_module(process, name):
    try:
        return process.modules.get_module(name)
    except KeyError:
        return load_module(process, name)


def load_module(process, name):
    modules = process.modules

    raw = api.to_native_string(name)
    path = raw.replace(".", os.sep)
    path = path + ".obn"
    script = None
    for directory in modules.path:
        filename = join_and_normalise_path(directory, path)
        if is_file(filename):
            script = load_file_content(filename)
            break

        if not script:
            raise ObinImportError(unicode(raw))

    return create_module(process, name, script)


def create_module(process, name, script):
    module = compile_module(process, name, script)
    process.run_module_force(module)
    process.modules.add_module(name, module)
    return module
