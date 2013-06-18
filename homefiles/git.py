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
            subprocess.check_call(['git'] + args)

    def _run(self, args):
        orig_path = os.getcwd()
        os.chdir(self.path)
        try:
            self.__run(args, dry_run=self.dry_run)
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

    def pull_origin(self):
        utils.log("Pulling origin", newline=False)
        self._run(['pull', 'origin', 'master'])
        utils.log("[DONE]")

    def push_origin(self):
        utils.log("Pushing origin", newline=False)
        self._run(['push', 'origin', 'master'])
        utils.log("[DONE]")

    @classmethod
    def clone(self, url, dry_run=False):
        utils.log("Cloning '%s'" % url, newline=False)
        self.__run(['clone', url], dry_run=dry_run)
        utils.log("[DONE]")


