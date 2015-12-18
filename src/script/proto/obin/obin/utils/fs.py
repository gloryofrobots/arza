__author__ = 'gloryofrobots'
import os
import os.path
import shutil
import distutils.dir_util
import filecmp


def abspath(path):
    return os.path.abspath(path)


def open_file(path, mode):
    return open(path, mode)


def get_file_extension(path):
    pathData = os.path.splitext(path)
    if len(pathData) != 2:
        return None

    ext = pathData[1]
    ext = ext[1:len(ext)]
    return ext.lower()


def set_file_extension(path, newExt):
    pathData = os.path.splitext(path)
    if len(pathData) != 2:
        return None

    basePart = pathData[0]
    return basePart + "." + newExt


def split_by_extension(path):
    return os.path.splitext(path)


def remove_file(path):
    os.remove(path)


def normalise_path(path):
    return os.path.normpath(path)


def get_path_difference(pathLarge, pathSmall):
    pathLargeN = normalise_path(pathLarge)
    pathSmallN = normalise_path(pathSmall)
    pathLargeN.replace(pathSmallN)


def path_step_backward(path, countSteps):
    result = normalise_path(path)

    while True:
        if countSteps <= 0:
            break

        countSteps -= 1
        result = get_dirname(result)

    return result


def join_path(path1, path2):
    path = os.path.join(path1, path2)
    return path


def join_and_normalise_path(path1, path2):
    path = os.path.join(path1, path2)
    path = normalise_path(path)
    return path


def get_dirname(path):
    dirname = os.path.dirname(path)
    return dirname


def get_basename(path):
    basename = os.path.basename(path)
    return basename


def split_path(path):
    parts = os.path.split(path)
    return parts


def is_directory(path):
    isDir = os.path.isdir(path)
    return isDir


def is_file(path):
    state = os.path.isfile(path)
    return state


def file_put_contents(filename, content, mode="wb"):
    try:
        file = open(filename, mode)
        file.write(content)
        file.close()
        return True

    except Exception:
        return False


def file_get_contents(filename):
    file = open(filename, "r")
    content = file.read()
    file.close()
    return content


def make_dirs_recursive_if_not_exist(path):
    if len(path) == 0:
        return

    if is_directory(path) is True:
        return

    make_dirs_recursive(path)


def make_dirs_recursive(path):
    os.makedirs(path)


def make_dir(path):
    os.mkdir(path)


def is_same_files(path1, path2):
    state = os.path.samefile(path1, path2)
    return state


def is_empty_dir(path):
    if len(os.listdir(path)) > 0:
        state = False
    else:
        state = True
    return state


def get_current_directory():
    curDir = os.getcwd()
    return curDir


def rename_file(old, new):
    os.rename(old, new)


def copy_file(fileSource, fileDestiny):
    shutil.copy(fileSource, fileDestiny)


def copytree(src, dst, ignore=None):
    if is_directory(dst) is False:
        os.makedirs(dst)

    names = os.listdir(src)

    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = join_path(src, name)
        dstname = join_path(dst, name)
        try:
            if is_directory(srcname):
                copytree(srcname, dstname, ignore)
            else:
                copy_file(srcname, dstname)

                # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Exception as err:
            errors.extend(err.args[0])

    if errors:
        raise Exception(errors)


def remove_dir_recursive(path):
    distutils.dir_util.remove_tree(path)


def copy_dir_recursive(directorySource, directoryDestiny, copyFileFunction=None, ignorePatterns=None):
    if is_directory(directoryDestiny) is False:
        os.makedirs(directoryDestiny)

    names = os.listdir(directorySource)

    if ignorePatterns is not None:
        ignore = shutil.ignore_patterns(ignorePatterns)
        ignored_names = ignore(directorySource, names)
    else:
        ignored_names = set()

    errors = []

    if copyFileFunction != None:
        chosenCopyFileFunction = copyFileFunction
    else:
        chosenCopyFileFunction = copy_file

    for name in names:
        if name in ignored_names:
            continue
        srcname = join_path(directorySource, name)
        dstname = join_path(directoryDestiny, name)
        try:
            if is_directory(srcname):
                copy_dir_recursive(srcname, dstname, copyFileFunction, ignorePatterns)
            else:
                chosenCopyFileFunction(srcname, dstname)

                # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])

    if errors:
        raise ValueError(errors)


def print_tree_difference(path1, path2):
    checkTrees = filecmp.dircmp(path1, path2)
    checkTrees.report_full_closure()
