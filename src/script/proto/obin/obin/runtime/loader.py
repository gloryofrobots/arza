__author__ = 'gloryofrobots'
from obin.objects.space import newmodule
from obin.objects import api
from obin.compile.compiler import compile
from obin.runtime.exception import ObinImportError
from obin.utils.fs import file_get_contents, is_file, join_and_normalise_path
import os


def compile_module(process, name, txt):
    code = compile(txt)
    module = newmodule(name, code)
    return module


def import_module(process, name):
    try:
        return process.get_module(name)
    except KeyError:
        return load_module(process, name)


def load_module(process, name):
    raw = api.tonativevalue(name)
    path = raw.replace(".", os.sep)
    script = None
    for directory in process.lib_dirs:
        filename = join_and_normalise_path(directory, path)
        if is_file(filename):
            script = file_get_contents(path)
            break

        if not script:
            raise ObinImportError(name)

    create_module(process, name, script)


def create_module(process, name, script):
    module = compile_module(name, script)
    process.run_module_force(module, None)
    process.add_module(name, module)
