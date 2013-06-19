import optparse
import os
import sys

import homefiles
import utils
import version


REPO_PATH = '~/.homefiles'
ROOT_PATH = '~'


def usage():
    prog = os.path.basename(sys.argv[0])
    commands = "[bundles|clone|init|link|sync|track|unlink|untrack]"
    return "%s [options] %s [filename]" % (prog, commands)


def main():
    parser = optparse.OptionParser(usage())
    parser.add_option("-d", "--dry-run",
                      action="store_true", dest="dry_run", default=False,
                      help="Don't actually make the changes")
    parser.add_option("-b", "--bundle",
                      action="store", dest="bundle",
                      help="Which bundle to use")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Turns on verbose output.")
    parser.add_option("--version",
                      action="store_true", dest="version", default=False,
                      help="Print version and exit")

    options, args = parser.parse_args()

    if options.version:
        print version.__version__
        return

    # --dry-run implies --verbose
    utils.LOG_VERBOSE = options.verbose or options.dry_run

    root_path = utils.truepath(ROOT_PATH)
    repo_path = utils.truepath(REPO_PATH)

    hf = homefiles.Homefiles(root_path, repo_path, dry_run=options.dry_run)
    bundles = hf.available_bundles()

    try:
        cmd = args[0]
    except IndexError:
        parser.print_help()
        print >> sys.stderr, usage()
        sys.exit(1)

    if cmd == 'bundles':
        for bundle in bundles:
            print '- %s' % bundle
    elif cmd == 'clone':
        try:
            origin = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)

        hf.clone(origin)
    elif cmd == 'init':
        hf.init()
    elif cmd == 'link':
        hf.link()
    elif cmd == 'sync':
        try:
            message = args[1]
        except IndexError:
            message = 'Sync'
        hf.sync(message=message)
    elif cmd == 'track':
        try:
            path = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)
        hf.track(path, bundle=bundle)
    elif cmd == 'unlink':
        hf.unlink()
    elif cmd == 'untrack':
        try:
            path = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)
        hf.untrack(path)
    else:
        print >> sys.stderr, "error: Unrecognized command '%s'" % cmd
        print >> sys.stderr, usage()
        sys.exit(1)
