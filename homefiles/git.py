import os
import subprocess

import utils


class GitRepo(object):
    def __init__(self, path, dry_run=False):
        self.path = path
        self.dry_run = dry_run

    @classmethod
    def __run(cls, args, dry_run=False):
        if not dry_run:
            proc = subprocess.Popen(['git'] + args, stdout=subprocess.PIPE)
            results = proc.communicate()
            if proc.returncode != 0:
                raise Exception('Nonzero return code: %d' % proc.returncode)
            return results

    def _run(self, args):
        orig_path = os.getcwd()
        os.chdir(self.path)
        try:
            return self.__run(args, dry_run=self.dry_run)
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
    def clone(self, url, dry_run=False):
        utils.log("Cloning '%s'" % url, newline=False)
        self.__run(['clone', url], dry_run=dry_run)
        utils.log("[DONE]")

    def uncommitted_changes(self):
        stdout, stderr = self.diff_index('HEAD')
        return len(stdout) != 0
