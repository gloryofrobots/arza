from obin.types import api
from obin.runtime import error
from obin.utils.fs import load_file_content, is_file, join_and_normalise_path
import os
from obin.types import space, api
from obin.compile import compiler


def import_module(process, name):
    try:
        return process.modules.get_module(api.to_s(name))
    except KeyError:
        return load_module(process, name)


def find_module_file(path, dirs):
    for directory in dirs:
        filename = join_and_normalise_path(directory, path)
        if is_file(filename):
            return filename

    return None


def load_module(process, name):
    modules = process.modules

    raw = api.to_s(name)
    path = "%s.obn" % raw.replace(".", os.sep)

    filename = find_module_file(path, modules.path)

    if not filename:
        return error.throw_1(error.Errors.IMPORT, name)

    return evaluate_module_file(process, name, filename)


def evaluate_module_file(process, name, filename):
    from obin.builtins.setup_globals import compile_module
    module = process.subprocess(space.newnativefunc(space.newsymbol(process, u"compile_module"), compile_module, 3),
                                space.newtuple([space.newstring_from_str(filename), name, process.modules.prelude.env]))

    process.modules.add_module(api.to_s(name), module)
    return module
    # script = load_file_content(filename)
    # sourcename = space.newsymbol_py_str(process, filename)
    #
    # module = compiler.compile_module(process, name, script, sourcename)
    # module.result = process.subprocess(module, space.newundefined())
    # process.modules.add_module(name, module)
    # return module
