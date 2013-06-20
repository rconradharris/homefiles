#!/usr/bin/env python
import os
import platform

import git
import utils

REMOTE_REPO = '.homefiles'


class HomefilesException(Exception):
    pass


class GitExecutableNotFound(HomefilesException):
    pass


class NotAuthorizedToClone(HomefilesException):
    pass


class RepoAlreadyExists(HomefilesException):
    pass


class SelectedBundlesNotFound(HomefilesException):
    pass


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

        if os.path.exists(os.path.join(path, '.trackeddir')):
            tracked = True
        elif path == '/':
            tracked = False
        else:
            tracked = self._is_directory_tracked(os.path.dirname(path))

        self.tracked_directories[path] = tracked
        return tracked

    def _track_directory(self, path):
        utils.log("Tracking directory '%s'" % path, newline=False)
        marker = os.path.join(path, '.trackeddir')
        if not self.dry_run:
            with open(marker, 'w') as f:
                pass
        utils.log("[DONE]")
        return marker

    def _matching_platforms(self):
        platforms = set()
        system = platform.system()
        if system:
            platforms.add(system)
            if system == 'Linux':
                distname, version, distid = platform.linux_distribution()
                if distname:
                    platforms.add(distname)
                    if version:
                        platforms.add('-'.join([distname, version]))

        return set('OS-%s' % p for p in platforms)

    def _present_bundles(self):
        return set(os.listdir(self.repo_path)) - set(['.git'])

    def _bundle_breakdown(self):
        default = set(['Default'])
        present = self._present_bundles()
        platform = set(b for b in present if b.startswith('OS-'))
        custom = present - platform - default
        platform_matches = self._matching_platforms()

        return default, platform, custom, platform_matches

    def _selected_bundles(self, selected):
        selected = selected or set()

        default, platform, custom, platform_matches = self._bundle_breakdown()

        available = default | platform | custom | platform_matches
        not_found = selected - available
        if not_found:
            raise SelectedBundlesNotFound(not_found)

        matches = default | platform_matches | selected | (custom & selected)
        return list(sorted(matches))

    def available_bundles(self):
        default, platform, custom, platform_matches = self._bundle_breakdown()

        available = default | platform | custom | platform_matches
        return list(sorted(available))

    def _walk_bundle(self, bundle):
        bundle_path = os.path.join(self.repo_path, bundle)
        if not os.path.exists(bundle_path):
            return

        for dirpath, dirnames, filenames in os.walk(bundle_path):
            if self._is_directory_tracked(dirpath):
                continue

            relpath = utils.relpath(bundle_path, dirpath)
            yield dirpath, dirnames, filenames, relpath

    def _link_bundle(self, bundle, undo_log):
        utils.log("Linking bundle '%s'" % bundle)

        for dirpath, dirnames, filenames, relpath in \
                self._walk_bundle(bundle):

            for dirname in dirnames:
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, relpath, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.symlink(src_dirpath, dst_dirpath,
                                  dry_run=self.dry_run, undo_log=undo_log)
                else:
                    utils.mkdir(dst_dirpath, dry_run=self.dry_run,
                                undo_log=undo_log)

            for filename in filenames:
                src_filename = os.path.join(dirpath, filename)
                dst_filename = os.path.join(self.root_path, relpath, filename)
                utils.symlink(src_filename, dst_filename,
                              dry_run=self.dry_run, undo_log=undo_log)

    def link(self, selected=None):
        undo_log = []
        try:
            for bundle in self._selected_bundles(selected):
                self._link_bundle(bundle, undo_log)
        except:
            # Ensure link is an atomic operation
            utils.undo_operations(undo_log, dry_run=self.dry_run)
            raise

    def _unlink_bundle(self, bundle, undo_log):
        utils.log("Unlinking bundle '%s'" % bundle)

        for dirpath, dirnames, filenames, relpath in \
                self._walk_bundle(bundle):

            for filename in filenames:
                file_path = os.path.join(self.root_path, relpath, filename)
                utils.remove_symlink(file_path, dry_run=self.dry_run,
                                     undo_log=undo_log)

            for dirname in dirnames:
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, relpath, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.remove_symlink(dst_dirpath, dry_run=self.dry_run,
                                         undo_log=undo_log)

    def unlink(self):
        undo_log = []
        try:
            for bundle in self.available_bundles():
                self._unlink_bundle(bundle, undo_log)
        except:
            # Ensure unlink is an atomic operation
            utils.undo_operations(undo_log, dry_run=self.dry_run)
            raise

    def track(self, path, bundle='Default'):
        """Track a file or a directory."""
        src_path = utils.truepath(path)
        is_directory = os.path.isdir(src_path)

        if self.root_path not in src_path:
            raise Exception('Cannot track files outside of root path')

        bundle_path = os.path.join(self.repo_path, bundle)
        dst_path = os.path.join(
            bundle_path, utils.relpath(self.root_path, src_path))

        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

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

        self.git.commit(message="Tracking '%s'" % path)

    def _populate_local_gitconfig(self, config):
        """If local gitconfig is empty populate it from global gitconfig."""

        # Get local
        local_config = self.git.config(
            config, local=True, ret_codes=[0, 1])[0].strip()

        if local_config:
            return

        # Get global
        global_config = self.git.config(
            config, global_=True, ret_codes=[0, 1])[0].strip()

        if not global_config:
            raise Exception("Unable to find '%s' in global gitconfig" %
                            config)

        # Set local to global
        self.git.config(config, global_config, local=True)

    def sync(self, message=None):
        if self.git.uncommitted_changes():
            self.git.commit(all=True, message=message)

        stdout, stderr = self.git.remote()
        if stdout is not None and 'origin' not in stdout:
            origin = raw_input('GitHub username or URL to repo: ')
            url = self._make_remote_url(origin)
            self.git.remote('add', 'origin', url)

        # The `unlink` operation that follows may potentially unlink our
        # global .gitconfig, making it impossible to generate a merge-commit.
        # To break out of this chicken-and-egg problem, we push the global
        # .gitconfig state into the local .gitconfig before it goes away
        self._populate_local_gitconfig('user.name')
        self._populate_local_gitconfig('user.email')

        self.unlink()
        try:
            self.git.pull_origin()
        finally:
            self.link()

        self.git.push_origin()

    def _make_remote_url(self, origin):
        if '://' in origin:
            url = origin
        else:
            data = dict(username=origin, repo=REMOTE_REPO)
            url = "git@github.com:%(username)s/%(repo)s.git" % data
        return url

    def clone(self, origin):
        url = self._make_remote_url(origin)

        try:
            self.git.clone(url, dry_run=self.dry_run)
        except git.NotAuthorizedToClone:
            raise NotAuthorizedToClone(
                'Permission denied. Add SSH key to GitHub.')
        except git.RepoAlreadyExists:
            raise RepoAlreadyExists('.homefiles repo already exists')
        except git.GitExecutableNotFound:
            raise GitExecutableNotFound('git needs to be installed first')

        repo_name = url.split('/')[-1].replace('.git', '')
        utils.rename(repo_name, self.repo_path, dry_run=self.dry_run)

    def init(self):
        if os.path.exists(self.repo_path):
            utils.warn("Homefiles repo already exists at '%s'"
                       % self.repo_path)
            return

        utils.mkdir(self.repo_path)
        self.git.init()

    def untrack(self, path):
        dst_path = utils.truepath(path)

        if not os.path.exists(dst_path):
            raise Exception("Path '%s' not found" % dst_path)

        if not os.path.islink(dst_path):
            raise Exception("Path '%s' is not a symlink" % dst_path)

        src_path = os.path.realpath(dst_path)

        try:
            utils.remove_symlink(dst_path, dry_run=self.dry_run)
            utils.rename(src_path, dst_path, dry_run=self.dry_run)
        except:
            utils.symlink(dst_path, src_path, dry_run=self.dry_run)

        self.git.rm(src_path)
        self.git.commit(message="Untracking '%s'" % path)
