import os
import sys

LOG_VERBOSE = False


class UtilException(Exception):
    pass


class NotASymlink(UtilException):
    pass


def capitalize_first_letter(s):
    return s[0].capitalize() + s[1:]


def log(msg, newline=True):
    if not LOG_VERBOSE:
        return

    if newline:
        print >> sys.stderr, msg
    else:
        print >> sys.stderr, msg,


def error(msg):
    print >> sys.stderr, 'ERROR: %s ' % msg


def warn(msg):
    print >> sys.stderr, 'WARNING: %s ' % msg


def truepath(path):
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


def relpath(base_path, dirpath):
    return dirpath.replace(os.path.commonprefix(
        [base_path, dirpath]), '').lstrip('/')


def symlink(source, link_name, dry_run=False, undo_log=None):
    log("Symlinking '%s' -> '%s'" % (source, link_name), newline=False)

    exists = os.path.exists(link_name)

    if exists and not os.path.islink(link_name):
        raise NotASymlink("'%s' is not a symlink. Remove file before linking."
                          % link_name)

    if exists:
        log("[SKIPPED]")
        return

    try:
        if not dry_run:
            os.symlink(source, link_name)
    except:
        log("[FAILED]")
        raise
    else:
        _add_undo_callback(
            undo_log, lambda: remove_symlink(link_name, dry_run=dry_run))
        log("[DONE]")


def mkdir(path, dry_run=False, undo_log=None):
    log("Creating directory '%s'" % path, newline=False)
    if os.path.exists(path):
        log("[SKIPPED]")
        return
    try:
        if not dry_run:
            os.mkdir(path)
    except:
        log("[FAILED]")
        raise
    else:
        _add_undo_callback(undo_log, lambda: rmdir(path, dry_run=dry_run))
        log("[DONE]")


def parent_directories(path):
    """Return a list of all parent directories for a path"""
    parents = []
    while path != '/':
        path = os.path.dirname(path)
        parents.append(path)
    parents.reverse()
    return parents


def makedirs(path, dry_run=False, undo_log=None):
    paths = parent_directories(path)
    paths.append(path)
    for create_path in paths:
        if not os.path.exists(create_path):
            mkdir(create_path, dry_run=dry_run, undo_log=undo_log)


def rmdir(path, dry_run=False, undo_log=None):
    log("Removing directory '%s'" % path, newline=False)
    if not os.path.exists(path):
        log("[SKIPPED]")
        return
    try:
        if not dry_run:
            os.rmdir(path)
    except:
        log("[FAILED]")
        raise
    else:
        _add_undo_callback(undo_log, lambda: mkdir(path, dry_run=dry_run))
        log("[DONE]")


def _add_undo_callback(undo_log, callback):
    if undo_log is not None:
        undo_log.append(callback)


def undo_operations(undo_log):
    log('Exception occured, rolling back...')
    while undo_log:
        callback = undo_log.pop()
        callback()


def rename(source, dest, dry_run=False, undo_log=None):
    log("Renaming '%s' -> '%s'" % (source, dest), newline=False)
    if os.path.exists(dest):
        log("[SKIPPED]")
        return
    try:
        if not dry_run:
            os.rename(source, dest)
    except:
        log("[FAILED]")
        raise
    else:
        _add_undo_callback(
            undo_log, lambda: rename(dest, source, dry_run=dry_run))
        log("[DONE]")


def remove_symlink(link_name, dry_run=False, undo_log=None):
    log("Removing symlink '%s'" % link_name, newline=False)
    if not os.path.exists(link_name):
        log("[SKIPPED]")
        return

    if not os.path.islink(link_name):
        raise NotASymlink("'%s' is not a symlink. Remove file before "
                          "unlinking." % link_name)

    source = os.path.realpath(link_name)

    if not dry_run:
        os.unlink(link_name)

    _add_undo_callback(
        undo_log, lambda: symlink(source, link_name, dry_run=dry_run))
    log("[DONE]")
