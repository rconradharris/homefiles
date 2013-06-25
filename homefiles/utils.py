import os
import sys

LOG_VERBOSE = False


class UtilException(Exception):
    pass


class NotASymlink(UtilException):
    pass


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
        _record_undo_operation(undo_log, 'symlink', link_name)
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
        _record_undo_operation(undo_log, 'mkdir', path)
        log("[DONE]")


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
        _record_undo_operation(undo_log, 'rmdir', path)
        log("[DONE]")


def _record_undo_operation(undo_log, operation, arg):
    if undo_log is not None:
        undo_log.append((operation, arg))


def undo_operations(undo_log, dry_run=False):
    if not undo_log:
        return

    # NOTE: when rolling back, we should not pass an undo_log into operations
    # because we don't want to get into an infinite loop of undo'ing things
    # we're undo'ing. Yo dawg.
    log('Exception occured, rolling back...')
    for operation, arg in reversed(undo_log):
        if operation == 'symlink':
            remove_symlink(arg, dry_run=dry_run)
        elif operation == 'mkdir':
            rmdir(arg, dry_run=dry_run)
        elif operation == 'remove_symlink':
            source, link_name = arg
            symlink(source, link_name, dry_run=dry_run)
        elif operation == 'rename':
            source, dest = arg
            rename(dest, source, dry_run=dry_run)
        else:
            raise Exception('Unknown undo operation %s' % operation)


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
        _record_undo_operation(undo_log, 'rename', (source, dest))
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

    _record_undo_operation(undo_log, 'remove_symlink', (source, link_name))
    log("[DONE]")
