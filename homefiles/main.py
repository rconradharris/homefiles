import optparse
import os
import sys

import homefiles
import utils
import version


DEFAULT_REMOTE_REPO = '.homefiles'
DEFAULT_REPO = '~/.homefiles'
DEFAULT_ROOT = '~'


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

    repo_path = utils.truepath(os.getenv('HOMEFILES_REPO') or DEFAULT_REPO)
    root_path = utils.truepath(os.getenv('HOMEFILES.ROOT') or DEFAULT_ROOT)
    remote_repo = os.getenv('HOMEFILES_REMOTE_REPO') or DEFAULT_REMOTE_REPO

    hf = homefiles.Homefiles(root_path, repo_path, remote_repo,
                             dry_run=options.dry_run)

    try:
        cmd = args[0]
    except IndexError:
        parser.print_help()
        print >> sys.stderr, usage()
        sys.exit(1)

    if cmd == 'bundles':
        matching, non_matching = hf.bundle_breakdown()
        print 'Match this machine:'
        for bundle in sorted(matching):
            print '- %s' % bundle

        print
        print 'Others:'
        for bundle in sorted(non_matching):
            print '- %s' % bundle
    elif cmd == 'clone':
        try:
            origin = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)
        try:
            hf.clone(origin)
        except homefiles.HomefilesException as e:
            utils.error(e)
            sys.exit(1)
    elif cmd == 'init':
        hf.init()
    elif cmd == 'link':
        if options.bundle:
            selected = [s.strip() for s in options.bundle.split(',')]
        else:
            selected = None

        try:
            hf.link(selected=selected)
        except homefiles.HomefilesException as e:
            utils.error(e)
            sys.exit(1)
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
        hf.track(path, bundle=options.bundle)
    elif cmd == 'unlink':
        try:
            hf.unlink()
        except homefiles.HomefilesException as e:
            utils.error(e)
            sys.exit(1)
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
