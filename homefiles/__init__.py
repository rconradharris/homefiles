#!/usr/bin/env python
import os
import platform

import git
import utils

REMOTE_REPO = '.homefiles'


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

    def _get_platforms(self):
        platforms = ['generic']
        system = platform.system()
        if system:
            platforms.append(system)
            if system == 'Linux':
                distro = platform.linux_distribution()
                if distro:
                    platforms.append(distro)

        return platforms

    def _link_bundle(self, platform):
        os_path = os.path.join(self.repo_path, platform)
        if not os.path.exists(os_path):
            return

        utils.log("Linking bundle '%s'" % platform)

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
        for platform in self._get_platforms():
            self._link_bundle(platform)

    def _unlink_bundle(self, platform):
        os_path = os.path.join(self.repo_path, platform)
        if not os.path.exists(os_path):
            return

        utils.log("Unlinking bundle '%s'" % platform)

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
        for platform in self._get_platforms():
            self._unlink_bundle(platform)

    def track(self, path, platform='generic'):
        """Track a file or a directory."""
        src_path = utils.truepath(path)
        is_directory = os.path.isdir(src_path)

        if self.root_path not in src_path:
            raise Exception('Cannot track files outside of root path')

        os_path = os.path.join(self.repo_path, platform)
        dst_path = os.path.join(
            os_path, utils.relpath(self.root_path, src_path))

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
            data = dict(username=origin, repo=REMOTE_REPO)
            url = "git@github.com:%(username)s/%(repo)s.git" % data

        self.git.clone(url, dry_run=self.dry_run)
        repo_name = url.split('/')[-1].replace('.git', '')
        utils.rename(repo_name, self.repo_path, dry_run=self.dry_run)
