from arza.types import api
from arza.runtime import error
from arza.misc.fs import load_file_content, is_file, join_and_normalise_path
import os
from arza.types import space, api
from arza.compile import compiler


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
    path = "%s.arza" % raw.replace(":", os.sep)

    filename = find_module_file(path, modules.path)
    # print "LOAD MODULE", name, filename

    if not filename:
        # in case import xxx:yyy:zzz
        # if zzz is dir then file
        # xxx/yyy/zzz/zzz.arza would be imported instead

        raw_list = raw.split(":")
        last_name = raw_list[len(raw_list)-1]
        path = "%s%s%s.arza" % (raw.replace(":", os.sep), os.sep, last_name)
        filename = find_module_file(path, modules.path)

    if not filename:
        return error.throw_1(error.Errors.IMPORT_ERROR, name)
    return evaluate_module_file(process, name, filename)


def evaluate_module_file(process, name, filename):
    from arza.builtins.lang import compile_module
    module = process.subprocess(space.newnativefunc(space.newsymbol(process, u"compile_module"), compile_module, 3),
                                space.newtuple([space.newstring_s(filename), name, process.modules.prelude]))

    if process.is_terminated():
        error.signal(module)
    process.modules.add_module(name, module)
    return module
