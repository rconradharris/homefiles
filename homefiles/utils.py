import os

LOG_VERBOSE = False


def log(msg, newline=True):
    if not LOG_VERBOSE:
        return

    if newline:
        print msg
    else:
        print msg,


def truepath(path):
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


def relpath(base_path, dirpath):
    return dirpath.replace(os.path.commonprefix(
        [base_path, dirpath]), '').lstrip('/')


def symlink(source, link_name, dry_run=False):
    log("Symlinking '%s' -> '%s'" % (source, link_name), newline=False)
    if os.path.exists(link_name):
        log("[SKIPPED]")
        return
    try:
        if not dry_run:
            os.symlink(source, link_name)
    except:
        log("[FAILED]")
        raise
    else:
        log("[DONE]")


def mkdir(path, dry_run=False):
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
        log("[DONE]")


def rename(src, dst, dry_run=False):
    log("Renaming '%s' -> '%s'" % (src, dst), newline=False)
    if os.path.exists(dst):
        log("[SKIPPED]")
        return
    try:
        if not dry_run:
            os.rename(src, dst)
    except:
        log("[FAILED]")
        raise
    else:
        log("[DONE]")


def remove_symlink(path, dry_run=False):
    log("Removing symlink '%s'" % path, newline=False)
    if not os.path.exists(path):
        log("[SKIPPED]")
        return
    if not os.path.islink(path):
        raise Exception("Path '%s' is not a symlink" % path)
    if not dry_run:
        os.unlink(path)
    log("[DONE]")
