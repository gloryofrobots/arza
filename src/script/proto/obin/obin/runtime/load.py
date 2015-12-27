from obin.objects import api
from obin.runtime.error import ObinImportError
from obin.utils.fs import load_file_content, is_file, join_and_normalise_path
import os


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

    return __setup_module(process, name, script)


def __setup_module(process, name, script):
    from obin.objects.space import newundefined
    from obin.compile.compiler import compile_module
    module = compile_module(process, name, script)
    module.result = process.subprocess(module, newundefined())
    process.modules.add_module(name, module)
    return module
