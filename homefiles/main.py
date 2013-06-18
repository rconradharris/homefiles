import os
import sys

import homefiles
import utils

REPO_PATH='~/.homefiles'
ROOT_PATH = '~'


def usage():
    prog = os.path.basename(sys.argv[0])
    utils.log("%s [--dry-run] [clone|link|sync|track|unlink] [filename]"
              % prog)
    sys.exit(1)


def main():
    dry_run = '--dry-run' in sys.argv
    root_path = utils.truepath(ROOT_PATH)
    repo_path = utils.truepath(REPO_PATH)

    hf = homefiles.Homefiles(root_path, repo_path, dry_run=dry_run)

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
