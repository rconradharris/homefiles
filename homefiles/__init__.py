#!/usr/bin/env python
import os
import sys

#REPO_LOCATION='~/.homefiles'
ROOT = '~'
REPO_LOCATION = '~/Documents/code/.homefiles'
DRY_RUN = True


def log(msg, newline=True):
    if newline:
        print msg
    else:
        print msg,


def usage():
    log("%s [clone|link|sync|track|unlink]" % os.path.basename(sys.argv[0]))
    sys.exit(1)



TRACKED_DIRECTORIES = {}

def is_directory_tracked(path):
    """A directory is tracked if it or one of its parents has a .trackeddir
    marker file.
    """
    try:
        return TRACKED_DIRECTORIES[path]
    except KeyError:
        pass
    TRACKED_DIRECTORIES[path] = tracked = os.path.exists(os.path.join(path, '.trackeddir'))
    if tracked:
        return True
    elif path == '/':
        return False
    else:
        return is_directory_tracked(os.path.dirname(path))


def symlink(source, link_name):
    log("Symlinking '%s' -> '%s'" % (source, link_name), newline=False)
    if os.path.exists(link_name):
        log("[SKIPPED]")
        return
    try:
        if not DRY_RUN:
            os.symlink(source, link_name)
    except:
        log("[FAILED]")
        raise
    else:
        log("[DONE]")


def mkdir(path):
    log("Creating directory '%s'" % path, newline=False)
    if os.path.exists(path):
        log("[SKIPPED]")
        return
    try:
        if not DRY_RUN:
            os.mkdir(path)
    except:
        log("[FAILED]")
        raise
    else:
        log("[DONE]")


def link(os_location):
    root = os.path.expanduser(ROOT)
    repo_location = os.path.expanduser(REPO_LOCATION)
    for dirpath, dirnames, filenames in os.walk(os_location):
        for dirname in dirnames:
            src_dirpath = os.path.join(dirpath, dirname)
            dst_dirpath = os.path.join(root, dirname)
            if is_directory_tracked(src_dirpath):
                symlink(src_dirpath, dst_dirpath)
            else:
                mkdir(dst_dirpath)

        if not is_directory_tracked(dirpath):
            for filename in filenames:
                relpath = dirpath.replace(os.path.commonprefix(
                    [os_location, dirpath]), '').lstrip('/')

                src_filename = os.path.join(dirpath, filename)
                dst_filename = os.path.join(root, relpath, filename)
                symlink(src_filename, dst_filename)


def main():
    root = os.path.expanduser(ROOT)
    repo_location = os.path.expanduser(REPO_LOCATION)

    generic_location = os.path.join(repo_location, 'generic')

    try:
        cmd = sys.argv[1]
    except IndexError:
        usage()

    if cmd == 'clone':
        raise NotImplementedError
    elif cmd == 'link':
        link(generic_location)
    elif cmd == 'sync':
        raise NotImplementedError
    elif cmd == 'track':
        raise NotImplementedError
    elif cmd == 'unlink':
        raise NotImplementedError
    else:
        log("error: Unrecognized command '%s'" % cmd)
        usage()
