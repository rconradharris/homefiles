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

    def commit_all(self, message):
        utils.log("Commiting all files", newline=False)
        self._run(['commit', '-a', '-m', message])
        utils.log("[DONE]")

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
