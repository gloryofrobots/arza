__author__ = 'gloryofrobots'
import os
# from .rlib import rpath as path
from os import path
import shutil
import distutils.dir_util
import filecmp


def abspath(p):
    return path.abspath(p)


def open_file(p, mode):
    return open(p, mode)


def get_file_extension(p):
    pathData = path.splitext(p)
    if len(pathData) != 2:
        return None

    ext = pathData[1]
    ext = ext[1:len(ext)]
    return ext.lower()


def set_file_extension(p, newExt):
    pathData = path.splitext(p)
    if len(pathData) != 2:
        return None

    basePart = pathData[0]
    return basePart + "." + newExt


def split_by_extension(p):
    return path.splitext(p)


def remove_file(p):
    os.remove(p)


def normalise_path(p):
    return path.normpath(p)


def get_path_difference(pathLarge, pathSmall):
    pathLargeN = normalise_path(pathLarge)
    pathSmallN = normalise_path(pathSmall)
    pathLargeN.replace(pathSmallN)


def path_step_backward(p, countSteps):
    result = normalise_path(p)

    while True:
        if countSteps <= 0:
            break

        countSteps -= 1
        result = get_dirname(result)

    return result


def join_path(path1, path2):
    return path.join(path1, path2)


def join_and_normalise_path(path1, path2):
    p = path.join(path1, path2)
    p = normalise_path(p)
    return p

def dirname(p):
    """Returns the directory component of a pathname"""
    i = p.rfind(os.sep) + 1
    assert i >= 0
    head = p[:i]
    if head and head != os.sep * len(head):
        head = head.rstrip(os.sep)
    return head

def get_dirname(p):
    dirname = path.dirname(p)
    return dirname


def get_basename(p):
    basename = path.basename(p)
    return basename


def split_path(p):
    parts = path.split(p)
    return parts


def is_directory(p):
    isDir = path.isdir(p)
    return isDir


def is_file(p):
    state = path.isfile(p)
    return state


def load_file_content(filename):
    from obin.misc.platform import streamio
    f = streamio.open_file_as_stream(str(filename))
    src = f.readall()
    return src


def make_dirs_recursive_if_not_exist(p):
    if len(p) == 0:
        return

    if is_directory(p) is True:
        return

    make_dirs_recursive(p)


def make_dirs_recursive(p):
    os.makedirs(p)


def make_dir(p):
    os.mkdir(p)


def is_same_files(path1, path2):
    state = path.samefile(path1, path2)
    return state


def is_empty_dir(p):
    if len(os.listdir(p)) > 0:
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
