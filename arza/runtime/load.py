from arza.types import api
from arza.runtime import error
from arza.misc.fs import load_file_content, is_file, join_and_normalise_path
import os
from arza.types import space, api
from arza.compile import compiler


def import_class(process, name):
    if process.classes.has_module(name):
        return process.classes.get_class(name)
    else:
        return load_class(process, name)


def import_class_by_name(process, script_name):
    result = import_class(process, space.newsymbol(process, script_name))
    if process.is_terminated():
        # error here
        return result
    return None


def find_class_file(path, dirs):
    # print "DIRS", dirs
    for directory in dirs:
        dir_s = api.to_s(directory)
        filename = join_and_normalise_path(dir_s, path)
        # print "TRY TO IMPORT", filename
        if is_file(filename):
            # print "SUCCESS"
            return filename

    return None


def get_class_filename(process, name):
    raw = api.to_s(name)
    path = "%s.arza" % raw.replace(".", os.sep)

    modules_path = process.classes.path
    filename = find_class_file(path, modules_path)
    # print "LOAD MODULE", name, filename

    if not filename:
        # in case import xxx:yyy:zzz
        # if zzz is dir then file
        # xxx/yyy/zzz/zzz.arza would be imported instead

        raw_list = raw.split(".")
        last_name = raw_list[len(raw_list) - 1]
        path = "%s%s%s.arza" % (raw.replace(".", os.sep), os.sep, last_name)
        filename = find_class_file(path, modules_path)

    if not filename:
        return error.throw_1(error.Errors.IMPORT_ERROR, name)

    return filename


def load_class(process, name):
    process.classes.before_load(name)
    filename = get_class_filename(process, name)
    return evaluate_class_file(process, name, filename)


def __evaluate_class_env(process, name, filename):
    from arza.builtins.lang import compile_module
    env = process.subprocess(space.newnativefunc(space.newsymbol(process, u"compile_module"), compile_module, 3),
                             space.newarray([space.newstring_s(filename), name, process.classes.prelude]))

    if process.is_terminated():
        error.signal(env)
    return env


def evaluate_class_file(process, name, filename):
    env = __evaluate_class_env(process, name, filename)
    base = process.std.classes.Object
    module = process.classes.add_env(base, env)
    return module
