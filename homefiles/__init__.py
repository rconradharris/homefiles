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
    prog = os.path.basename(sys.argv[0])
    log("%s [clone|link|sync|track|unlink] [filename]" % prog)
    sys.exit(1)


def truepath(path):
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


def relpath(base_path, dirpath):
    return dirpath.replace(os.path.commonprefix(
        [base_path, dirpath]), '').lstrip('/')


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


def track_directory(path):
    log("Tracking directory '%s'" % path, newline=False)
    marker = os.path.join(path, '.trackeddir')
    if not DRY_RUN:
        with open(marker) as f:
            pass
    log("[DONE]")
    return marker


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


def rename(src, dst):
    log("Renaming '%s' -> '%s'" % (src, dst), newline=False)
    if os.path.exists(dst):
        log("[SKIPPED]")
        return
    try:
        if not DRY_RUN:
            os.rename(src, dst)
    except:
        log("[FAILED]")
        raise
    else:
        log("[DONE]")
    pass


class GitRepo(object):
    def __init__(self, path):
        self.path = path

    def _run(self, args):
        if not DRY_RUN:
            orig_path = os.getcwd()
            os.chdir(self.path)
            try:
                subprocess.check_call(['git'] + args)
            finally:
                os.chdir(orig_path)

    def add(self, path):
        log("Adding '%s' to Git" % path, newline=False)
        self._run(['add', path])
        log("[DONE]")

    def commit_all(self, message):
        log("Commiting all files", newline=False)
        self._run(['commit', '-a', '-m', message])
        log("[DONE]")

    def pull_origin(self):
        log("Pulling origin", newline=False)
        self._run(['pull', 'origin', 'master'])
        log("[DONE]")

    def push_origin(self):
        log("Pushing origin", newline=False)
        self._run(['push', 'origin', 'master'])
        log("[DONE]")


class Homefiles(object):
    def __init__(self, root_path, repo_path):
        self.root_path = root_path
        self.repo_path = repo_path
        self.git = GitRepo(repo_path)

    def _get_os_names(self):
        return [p for p in os.listdir(self.repo_path)
                if p != '.git' and os.path.isdir(os.path.join(self.repo_path, p))]

    def _link_os_bundle(self, os_name):
        """Symlink all the things."""
        log("Linking bundle '%s'" % os_name)
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
                    src_filename = os.path.join(dirpath, filename)
                    dst_filename = os.path.join(
                            self.root_path, relpath(os_path, dirpath),
                            filename)
                    symlink(src_filename, dst_filename)

    def link(self):
        for os_name in self._get_os_names():
            self._link_os_bundle(os_name)

    def track(self, path, os_name='generic'):
        """Track a file or a directory."""
        src_path = truepath(path)
        is_directory = os.path.isdir(src_path)

        if self.root_path not in src_path:
            raise Exception('Cannot track files outside of root path')

        os_path = os.path.join(self.repo_path, os_name)
        dst_path = os.path.join(os_path, relpath(self.root_path, src_path))

        try:
            rename(src_path, dst_path)
            symlink(dst_path, src_path)
        except:
            rename(dst_path, src_path)
            raise

        self.git.add(dst_path)

        if is_directory:
            marker = track_directory(dst_path)
            self.git.add(marker)

    def sync(self, message):
        self.git.commit_all(message)
        self.git.pull_origin()
        self.git.push_origin()


def main():
    root_path = truepath(ROOT_PATH)
    repo_path = truepath(REPO_PATH)

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
        try:
            message = sys.argv[2]
        except IndexError:
            message = 'Sync'
        homefiles.sync(message)
    elif cmd == 'track':
        try:
            path = sys.argv[2]
        except IndexError:
            usage()
        homefiles.track(path)
    elif cmd == 'unlink':
        raise NotImplementedError
    else:
        log("error: Unrecognized command '%s'" % cmd)
        usage()
