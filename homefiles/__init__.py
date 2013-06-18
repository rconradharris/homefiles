#!/usr/bin/env python
import os
import sys

#REPO_PATH='~/.homefiles'
ROOT_PATH = '~'
REPO_PATH = '~/Documents/code/.homefiles'
DRY_RUN = True
OS_NAME = 'generic'

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


class Homefiles(object):
    def __init__(self, root_path, repo_path):
        self.root_path = root_path
        self.repo_path = repo_path

    def _get_os_names(self):
        return [p for p in os.listdir(self.repo_path)
                if p != '.git' and os.path.isdir(os.path.join(self.repo_path, p))]

    def _link_os_bundle(self, os_name):
        """Symlink all the things."""
        log("Linking bundle '%s'" % os.name)
        os_path = os.path.join(self.repo_path, os_name)

        for dirpath, dirnames, filenames in os.walk(os_path):
            for dirname in dirnames:
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, dirname)
                if is_directory_tracked(src_dirpath):
                    symlink(src_dirpath, dst_dirpath)
                else:
                    mkdir(dst_dirpath)

            if not is_directory_tracked(dirpath):
                for filename in filenames:
                    relpath = dirpath.replace(os.path.commonprefix(
                        [os_path, dirpath]), '').lstrip('/')

                    src_filename = os.path.join(dirpath, filename)
                    dst_filename = os.path.join(
                            self.root_path, relpath, filename)
                    symlink(src_filename, dst_filename)

    def link(self):
        for os_name in self._get_os_names():
            self._link_os_bundle(os_name)

    def track(self, path):
        """Track a file or a directory."""
        pass


def main():
    root_path = os.path.expanduser(ROOT_PATH)
    repo_path = os.path.expanduser(REPO_PATH)

    homefiles = Homefiles(root_path, repo_path)

    try:
        cmd = sys.argv[1]
    except IndexError:
        usage()

    if cmd == 'clone':
        raise NotImplementedError
    elif cmd == 'link':
        homefiles.link()
    elif cmd == 'sync':
        raise NotImplementedError
    elif cmd == 'track':
        raise NotImplementedError
    elif cmd == 'unlink':
        raise NotImplementedError
    else:
        log("error: Unrecognized command '%s'" % cmd)
        usage()
