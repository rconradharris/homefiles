#!/usr/bin/env python
import os
import sys

import git
import utils

#REPO_PATH='~/.homefiles'
ROOT_PATH = '~'
REPO_PATH = '~/Documents/code/.homefiles'
REMOTE_REPO = '.homefiles'

DRY_RUN = True
OS_NAME = 'generic'


class Homefiles(object):
    def __init__(self, root_path, repo_path, dry_run=False):
        self.root_path = root_path
        self.repo_path = repo_path
        self.dry_run = dry_run
        self.git = git.GitRepo(repo_path, dry_run=self.dry_run)
        self.tracked_directories = {}

    def _is_directory_tracked(self, path):
        """A directory is tracked if it or one of its parents has a .trackeddir
        marker file.
        """
        try:
            return self.tracked_directories[path]
        except KeyError:
            pass
        self.tracked_directories[path] = tracked = os.path.exists(
                os.path.join(path, '.trackeddir'))
        if tracked:
            return True
        elif path == '/':
            return False
        else:
            return self._is_directory_tracked(os.path.dirname(path))

    def _track_directory(self, path):
        utils.log("Tracking directory '%s'" % path, newline=False)
        marker = os.path.join(path, '.trackeddir')
        if not self.dry_run:
            with open(marker) as f:
                pass
        utils.log("[DONE]")
        return marker

    def _get_os_names(self):
        return [p for p in os.listdir(self.repo_path)
                if p != '.git' and os.path.isdir(os.path.join(self.repo_path, p))]

    def _link_os_bundle(self, os_name):
        utils.log("Linking bundle '%s'" % os_name)
        os_path = os.path.join(self.repo_path, os_name)

        for dirpath, dirnames, filenames in os.walk(os_path):
            for dirname in dirnames:
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.symlink(src_dirpath, dst_dirpath,
                            dry_run=self.dry_run)
                else:
                    utils.mkdir(dst_dirpath, dry_run=self.dry_run)

            if not self._is_directory_tracked(dirpath):
                for filename in filenames:
                    src_filename = os.path.join(dirpath, filename)
                    dst_filename = os.path.join(
                            self.root_path, utils.relpath(os_path, dirpath),
                            filename)
                    utils.symlink(src_filename, dst_filename,
                            dry_run=self.dry_run)

    def link(self):
        for os_name in self._get_os_names():
            self._link_os_bundle(os_name)

    def _unlink_os_bundle(self, os_name):
        utils.log("Unlinking bundle '%s'" % os_name)
        os_path = os.path.join(self.repo_path, os_name)

        for dirpath, dirnames, filenames in os.walk(os_path):
            if not self._is_directory_tracked(dirpath):
                for filename in filenames:
                    file_path = os.path.join(
                            self.root_path, utils.relpath(os_path, dirpath),
                            filename)
                    utils.remove_symlink(file_path, dry_run=self.dry_run)

            for dirname in dirnames:
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.remove_symlink(dst_dirpath, dry_run=self.dry_run)

    def unlink(self):
        for os_name in self._get_os_names():
            self._unlink_os_bundle(os_name)

    def track(self, path, os_name='generic'):
        """Track a file or a directory."""
        src_path = utils.truepath(path)
        is_directory = os.path.isdir(src_path)

        if self.root_path not in src_path:
            raise Exception('Cannot track files outside of root path')

        os_path = os.path.join(self.repo_path, os_name)
        dst_path = os.path.join(os_path, utils.relpath(self.root_path, src_path))

        try:
            utils.rename(src_path, dst_path, dry_run=self.dry_run)
            utils.symlink(dst_path, src_path, dry_run=self.dry_run)
        except:
            utils.rename(dst_path, src_path, dry_run=self.dry_run)
            raise

        self.git.add(dst_path)

        if is_directory:
            marker = self._track_directory(dst_path)
            self.git.add(marker)

    def sync(self, message):
        self.git.commit_all(message)
        self.git.pull_origin()
        self.git.push_origin()

    def clone(self, origin):
        if '://' in origin:
            url = origin
        else:
            url = "git@github.com:%(username)s/%(repo)s.git" % dict(
                    username=origin, repo=REMOTE_REPO)
        self.git.clone(url, dry_run=self.dry_run)
        utils.rename(REMOTE_REPO, self.repo_path, dry_run=self.dry_run)


def usage():
    prog = os.path.basename(sys.argv[0])
    utils.log("%s [clone|link|sync|track|unlink] [filename]" % prog)
    sys.exit(1)


def main():
    root_path = utils.truepath(ROOT_PATH)
    repo_path = utils.truepath(REPO_PATH)

    homefiles = Homefiles(root_path, repo_path, dry_run=DRY_RUN)

    try:
        cmd = sys.argv[1]
    except IndexError:
        usage()

    if cmd == 'clone':
        try:
            origin = sys.argv[2]
        except IndexError:
            usage()
        homefiles.clone(origin)
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
        homefiles.unlink()
    else:
        utils.log("error: Unrecognized command '%s'" % cmd)
        usage()
