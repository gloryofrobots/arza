from lalan.types import api
from lalan.runtime import error
from lalan.misc.fs import load_file_content, is_file, join_and_normalise_path
import os
from lalan.types import space, api
from lalan.compile import compiler


def import_module(process, name):
    if process.modules.has_module(name):
        return process.modules.get_module(name)
    else:
        return load_module(process, name)

def import_module_by_name(process, script_name):
    result = import_module(process, space.newsymbol(process, script_name))
    if process.is_terminated():
        # error here
        return result
    return None

def find_module_file(path, dirs):
    # print "DIRS", dirs
    for directory in dirs:
        dir_s = api.to_s(directory)
        filename = join_and_normalise_path(dir_s, path)
        # print "TRY TO IMPORT", filename
        if is_file(filename):
            # print "SUCCESS"
            return filename

    return None


def load_module(process, name):
    modules = process.modules
    modules.before_load(name)
    raw = api.to_s(name)
    path = "%s.lal" % raw.replace(":", os.sep)

    filename = find_module_file(path, modules.path)

    if not filename:
        return error.throw_1(error.Errors.IMPORT_ERROR, name)

    return evaluate_module_file(process, name, filename)


def evaluate_module_file(process, name, filename):
    from lalan.builtins.lang import compile_module
    module = process.subprocess(space.newnativefunc(space.newsymbol(process, u"compile_module"), compile_module, 3),
                                space.newtuple([space.newstring_s(filename), name, process.modules.prelude]))

    if process.is_terminated():
        error.signal(module)
    process.modules.add_module(name, module)
    return module
