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
    return "%s [options] [clone|link|sync|track|unlink] [filename]" % prog


def main():
    parser = optparse.OptionParser(usage())
    parser.add_option("-a", "--available-platforms",
                      action="store_true", dest="available_platforms",
                      default=False,
                      help="Print available platforms for this machine"
                           " and exit.")
    parser.add_option("-d", "--dry-run",
                      action="store_true", dest="dry_run", default=False,
                      help="Don't actually make the changes")
    parser.add_option("-p", "--platform",
                      action="store", dest="platform",
                      help="Which platform to use. (Defaults to best guess)")
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

    utils.LOG_VERBOSE = options.verbose

    root_path = utils.truepath(ROOT_PATH)
    repo_path = utils.truepath(REPO_PATH)

    hf = homefiles.Homefiles(root_path, repo_path, dry_run=options.dry_run)
    platforms = hf.available_platforms()

    if options.available_platforms:
        print 'Platforms available for this machine:'
        for platform in platforms:
            print '- %s' % platform
        return

    try:
        cmd = args[0]
    except IndexError:
        parser.print_help()
        print >> sys.stderr, usage()
        sys.exit(1)

    if cmd == 'clone':
        try:
            origin = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)

        hf.clone(origin)
    elif cmd == 'link':
        hf.link()
    elif cmd == 'sync':
        try:
            message = args[1]
        except IndexError:
            message = 'Sync'
        hf.sync(message)
    elif cmd == 'track':
        try:
            path = args[1]
        except IndexError:
            print >> sys.stderr, usage()
            sys.exit(1)

        if options.platform:
            platform = options.platform.capitalize()
        else:
            platform = 'Generic'

        if platform not in platforms:
            print >> sys.stderr, "warning: Platform '%s' is not supported" \
                                 " by this machine" % platform

        hf.track(path, platform=platform)
    elif cmd == 'unlink':
        hf.unlink()
    else:
        print >> sys.stderr, "error: Unrecognized command '%s'" % cmd
        print >> sys.stderr, usage()
        sys.exit(1)
