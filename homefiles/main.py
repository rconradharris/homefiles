import os
import sys

import homefiles
import utils

#REPO_PATH='~/.homefiles'
REPO_PATH = '~/Documents/code/.homefiles'

ROOT_PATH = '~'
OS_NAME = 'generic'

DRY_RUN = True


def usage():
    prog = os.path.basename(sys.argv[0])
    utils.log("%s [clone|link|sync|track|unlink] [filename]" % prog)
    sys.exit(1)


def main():
    root_path = utils.truepath(ROOT_PATH)
    repo_path = utils.truepath(REPO_PATH)

    hf = homefiles.Homefiles(root_path, repo_path, dry_run=DRY_RUN)

    try:
        cmd = sys.argv[1]
    except IndexError:
        usage()

    if cmd == 'clone':
        try:
            origin = sys.argv[2]
        except IndexError:
            usage()
        hf.clone(origin)
    elif cmd == 'link':
        hf.link()
    elif cmd == 'sync':
        try:
            message = sys.argv[2]
        except IndexError:
            message = 'Sync'
        hf.sync(message)
    elif cmd == 'track':
        try:
            path = sys.argv[2]
        except IndexError:
            usage()
        hf.track(path)
    elif cmd == 'unlink':
        hf.unlink()
    else:
        utils.log("error: Unrecognized command '%s'" % cmd)
        usage()
