from obin.types import api
from obin.runtime.error import ObinImportError
from obin.utils.fs import load_file_content, is_file, join_and_normalise_path
import os
from obin.types import space
from obin.compile import compiler


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
    filename = None
    for directory in modules.path:
        filename = join_and_normalise_path(directory, path)
        if is_file(filename):
            break

    if not filename:
        raise ObinImportError(unicode(raw))

    return __setup_module(process, name, filename)


def __setup_module(process, name, filename):
    script = load_file_content(filename)
    sourcename = space.newsymbol_py_str(process, filename)

    module = compiler.compile_module(process, name, script, sourcename)
    module.result = process.subprocess(module, space.newundefined())
    process.modules.add_module(name, module)
    return module
