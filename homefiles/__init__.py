#!/usr/bin/env python
import fnmatch
import os
import platform

import git
import utils


IGNORE = [
    '.DS_Store',
]


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


class NotASymlink(HomefilesException):
    pass


class CustomBundleState(object):
    """Records which custom bundles have been applied so that if we need to
    re-link during a `sync` operation, we'll know which bundles to re-apply.
    """
    def __init__(self, repo_path):
        self.path = os.path.join(repo_path, '.git', 'homefiles-custom-bundles')

    def clear(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def read(self):
        if not os.path.exists(self.path):
            return []

        bundles = []
        with open(self.path) as f:
            for line in f:
                bundle = line.strip()
                bundles.append(bundle)

        return bundles

    def append(self, bundle):
        existing = set(self.read())
        with open(self.path, 'a') as f:
            if bundle not in existing:
                f.write('%s\n' % bundle)


class Homefiles(object):
    def __init__(self, root_path, repo_path, remote_repo, dry_run=False):
        self.root_path = root_path
        self.repo_path = repo_path
        self.remote_repo = remote_repo
        self.dry_run = dry_run
        self.git = git.GitRepo(repo_path, dry_run=self.dry_run)
        self.tracked_directories = {}
        self.custom_bundle_state = CustomBundleState(repo_path)

    def _is_directory_tracked(self, path):
        """A directory is tracked if it or one of its parents has a .trackeddir
        marker file.
        """
        # TODO: this could be rewritten to not be recursive and instead use
        # utils.parent_directories
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
        """Return platforms available for this machine going from most
        specific to least specific.
        """
        platforms = []
        system = platform.system()
        if system:
            # Systems appear to be capitalized, but adding explicit
            # capitalization anyway just in case that ever changes
            system = utils.capitalize_first_letter(system)
            platforms.append(system)
            if system == 'Linux':
                distname, version, distid = platform.linux_distribution()
                if distname:
                    # Some distributions are capitalized (Ubuntu) others are
                    # all lowercase (debian).
                    distname = utils.capitalize_first_letter(distname)
                    platforms.append(distname)
                    if version:
                        platforms.append('-'.join([distname, version]))

        platforms.reverse()
        return ['OS-%s' % p for p in platforms]

    def _present_bundles(self):
        return [b for b in os.listdir(self.repo_path) if b != '.git']

    def _is_custom_bundle(self, bundle):
        return bundle != 'Default' and not bundle.startswith('OS-')

    def _selected_bundles(self, selected):
        """Return an ordered list of bundles from most-specific to
        least-specific that match the selected criteria.
        """
        selected = selected or []

        default = ['Default']
        present = self._present_bundles()
        platform = self._matching_platforms()

        # Ensure all selected bundles are available
        not_found = set(selected) - set(default + present + platform)
        if not_found:
            raise SelectedBundlesNotFound('Could not find these bundles: %s'
                                          % ', '.join(not_found))

        # Uniquify results
        seen = set()
        ordered_matches = []
        for bundle in selected + platform + default:
            if bundle in seen:
                continue
            ordered_matches.append(bundle)
            seen.add(bundle)

        return ordered_matches

    def bundle_breakdown(self):
        default = set(['Default'])
        platform = set(self._matching_platforms())
        custom = set(self.custom_bundle_state.read())
        present = set(self._present_bundles())

        matching = default | platform | custom
        non_matching = present - matching

        return matching, non_matching

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
                if self._ignore_match(dirname):
                    continue
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, relpath, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.symlink(src_dirpath, dst_dirpath,
                                  dry_run=self.dry_run, undo_log=undo_log)
                else:
                    utils.mkdir(dst_dirpath, dry_run=self.dry_run,
                                undo_log=undo_log)

            for filename in filenames:
                if self._ignore_match(filename):
                    continue
                src_filename = os.path.join(dirpath, filename)
                dst_filename = os.path.join(self.root_path, relpath, filename)
                utils.symlink(src_filename, dst_filename,
                              dry_run=self.dry_run, undo_log=undo_log)

    def link(self, selected=None):
        undo_log = []
        for bundle in self._selected_bundles(selected):
            try:
                self._link_bundle(bundle, undo_log)
            except utils.NotASymlink as e:
                utils.undo_operations(undo_log)
                raise NotASymlink(str(e))
            except:
                utils.undo_operations(undo_log)
                raise
            else:
                if self._is_custom_bundle(bundle):
                    self.custom_bundle_state.append(bundle)

    def _ignore_match(self, filename):
        for pattern in IGNORE:
            print filename, pattern
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def _unlink_bundle(self, bundle, undo_log):
        utils.log("Unlinking bundle '%s'" % bundle)

        for dirpath, dirnames, filenames, relpath in \
                self._walk_bundle(bundle):

            for filename in filenames:
                if self._ignore_match(filename):
                    continue
                file_path = os.path.join(self.root_path, relpath, filename)
                utils.remove_symlink(file_path, dry_run=self.dry_run,
                                     undo_log=undo_log)

            for dirname in dirnames:
                if self._ignore_match(dirname):
                    continue
                src_dirpath = os.path.join(dirpath, dirname)
                dst_dirpath = os.path.join(self.root_path, relpath, dirname)
                if self._is_directory_tracked(src_dirpath):
                    utils.remove_symlink(dst_dirpath, dry_run=self.dry_run,
                                         undo_log=undo_log)

    def unlink(self, clear_custom_bundle_state=True):
        undo_log = []
        matching, non_matching = self.bundle_breakdown()
        for bundle in sorted(matching | non_matching):
            try:
                self._unlink_bundle(bundle, undo_log)
            except utils.NotASymlink as e:
                utils.undo_operations(undo_log)
                raise NotASymlink(str(e))
            except:
                utils.undo_operations(undo_log)
                raise

        if clear_custom_bundle_state:
            self.custom_bundle_state.clear()

    def track(self, path, bundle=None):
        """Track a file or a directory."""
        # We don't use kwarg default, because None represents default to
        # callers
        bundle = bundle or 'Default'
        src_path = utils.truepath(path)
        is_directory = os.path.isdir(src_path)

        if self.root_path not in src_path:
            raise Exception('Cannot track files outside of root path')

        bundle_path = os.path.join(self.repo_path, bundle)
        dst_path = os.path.join(
            bundle_path, utils.relpath(self.root_path, src_path))

        undo_log = []

        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            utils.makedirs(dst_dir, dry_run=self.dry_run, undo_log=undo_log)

        try:
            utils.rename(src_path, dst_path, dry_run=self.dry_run,
                         undo_log=undo_log)
            try:
                utils.symlink(dst_path, src_path, dry_run=self.dry_run)
            except:
                utils.undo_operations(undo_log)
                raise
        except:
            utils.undo_operations(undo_log)
            raise

        self.git.add(dst_path)

        if is_directory:
            marker = self._track_directory(dst_path)
            self.git.add(marker)

        self.git.commit(message="Tracking '%s'" % path)

    def _populate_local_gitconfig(self, config):
        """If local gitconfig is empty populate it from global gitconfig."""
        if self.dry_run:
            return

        # Get local
        local_config = self.git.config(
            config, ret_codes=[0, 1])[0].strip()

        if local_config:
            return

        # Get global
        global_config = self.git.config(
            config, global_=True, ret_codes=[0, 1])[0].strip()

        if not global_config:
            raise Exception("Unable to find '%s' in global gitconfig" %
                            config)

        # Set local to global
        self.git.config(config, global_config)

    def _relink(self):
        # Bundles may have been removed, so only relink bundles that still
        # exist
        custom_bundles = [b for b in self.custom_bundle_state.read() if
                          os.path.exists(os.path.join(self.repo_path, b))]

        utils.log('Relinking custom bundles: %s' % custom_bundles)
        self.link(selected=custom_bundles)

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

        self.unlink(clear_custom_bundle_state=False)
        try:
            self.git.pull_origin()
        finally:
            self._relink()

        self.git.push_origin()

    def _make_remote_url(self, origin):
        if '://' in origin:
            url = origin
        else:
            data = dict(username=origin, repo=self.remote_repo)
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

        undo_log = []
        utils.remove_symlink(dst_path, dry_run=self.dry_run, undo_log=undo_log)
        try:
            utils.rename(src_path, dst_path, dry_run=self.dry_run)
        except:
            utils.undo_operations(undo_log)
            raise

        self.git.rm(src_path)
        self.git.commit(message="Untracking '%s'" % path)

    def diff(self):
        self.git.diff(capture_output=False)
