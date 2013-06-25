import errno
import os
import subprocess

import utils


class ProcessException(Exception):
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

        message = "returncode=%d stdout='%s' stderr='%s'" % (
            returncode, stdout, stderr)

        super(ProcessException, self).__init__(message)


class GitException(Exception):
    pass


class GitExecutableNotFound(GitException):
    pass


class NotAuthorizedToClone(GitException):
    pass


class RepoAlreadyExists(GitException):
    pass


class RawGitRepo(object):
    def __init__(self, path, dry_run=False):
        self.path = path
        self.dry_run = dry_run

    @classmethod
    def __run(cls, args, dry_run=False, ret_codes=None):
        ret_codes = ret_codes or [0]
        results = None, None

        if not dry_run:
            try:
                proc = subprocess.Popen(['git'] + args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    raise GitExecutableNotFound
                raise

            stdout, stderr = proc.communicate()

            if proc.returncode not in ret_codes:
                raise ProcessException(proc.returncode, stdout, stderr)

        return stdout, stderr

    def _run(self, args, ret_codes=None):
        orig_path = os.getcwd()
        os.chdir(self.path)
        try:
            return self.__run(args, dry_run=self.dry_run, ret_codes=ret_codes)
        finally:
            os.chdir(orig_path)

    def add(self, path):
        utils.log("Adding '%s' to Git" % path, newline=False)
        self._run(['add', path])
        utils.log("[DONE]")

    def rm(self, path):
        utils.log("Removing '%s' from Git" % path, newline=False)
        self._run(['rm', path])
        utils.log("[DONE]")

    def config(self, config, *args, **kwargs):
        cmd_args = ['config']
        if kwargs.get('global_', False):
            cmd_args.append('--global')
        cmd_args.append(config)
        cmd_args.extend(args)
        utils.log("Configuring %s in Git" % config, newline=False)
        results = self._run(cmd_args, ret_codes=kwargs.get('ret_codes'))
        utils.log("[DONE]")
        return results

    def commit(self, all=False, message=None):
        args = ['commit']
        if all:
            args.append('-a')
        if message:
            args.extend(['-m', message])
        utils.log("Commiting to Git", newline=False)
        self._run(args)
        utils.log("[DONE]")

    def diff_index(self, treeish):
        utils.log("Diffing index to %s" % treeish, newline=False)
        results = self._run(['diff-index', treeish])
        utils.log("[DONE]")
        return results

    def init(self):
        utils.log("Initializing repo at '%s'" % self.path, newline=False)
        self._run(['init', '.'])
        utils.log("[DONE]")

    def pull_origin(self):
        utils.log("Pulling origin", newline=False)
        self._run(['pull', 'origin', 'master'])
        utils.log("[DONE]")

    def push_origin(self):
        utils.log("Pushing origin", newline=False)
        self._run(['push', 'origin', 'master'])
        utils.log("[DONE]")

    def remote(self, *args, **kwargs):
        cmd_args = ['remote']
        if kwargs.get('verbose', False):
            cmd_args.append('-v')
        cmd_args.extend(args)
        return self._run(cmd_args)

    @classmethod
    def clone(cls, url, dry_run=False):
        cls.__run(['clone', url], dry_run=dry_run)


class GitRepo(RawGitRepo):
    @classmethod
    def clone(cls, url, dry_run=False):
        utils.log("Cloning '%s'" % url, newline=False)

        try:
            return super(GitRepo, cls).clone(url, dry_run=dry_run)
        except ProcessException as e:
            if 'Permission denied (publickey)' in e.stderr:
                raise NotAuthorizedToClone
            elif 'already exists and is not an empty directory':
                raise RepoAlreadyExists
            else:
                raise

        utils.log("[DONE]")

    def uncommitted_changes(self):
        stdout, stderr = self.diff_index('HEAD')
        if stdout is None:
            return False
        return len(stdout) != 0
