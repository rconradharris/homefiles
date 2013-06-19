=========
homefiles
=========


Features
========

    * Track files or directories
    * Easily clone files to another machine
    * Sync updates back to GitHub
    * Handle platform specific files


Getting Started
===============

Install::

    pip install homefiles


Track Your Files::

    homefiles init
    homefiles track ~/.vimrc


Sync Your Files To GitHub::

    homefiles sync 'Added vimrc'


Clone Your Files From Another Machine::

    homefiles clone rconradharris
    homefiles link


Repo Layout
===========

The repo is divided into multiple bundles, one for each platform you intend to
use.

Within the bundle, the layout is relative to your home directory, so
``Generic/bin/foo.sh`` will be symlinked as ``$HOME/bin/foo.sh`` for all
platforms. In contrast, ``Darwin/Documents/code/mac_only.sh`` will symlink to
``$HOME/Documents/code/mac_only.sh`` only on Macs.

If a whole directory is being tracked, the ``.trackeddir`` marker file will be
present in it. This will cause the directory to be symlinked as a single unit,
rather than symlinking the individual files.

::

    .homefiles/
        Generic/
            .vimrc
            bin/
                all_platforms.sh
        Darwin/
            Documents/
                code/
                    mac_only.sh
                notes/
                    .trackeddir
        Linux/
            bin/
                linux_only.sh
        Ubuntu/
            bin/
                ubuntu_only.sh
        Ubuntu-13.04/
            bin/
                raring_only.sh


Advanced
========


Determine available platforms for current machine::

    $ homefiles -a
    Platforms available for this machine:
    - Generic
    - Darwin

    $ homefiles -a
    Platforms available for this machine:
    - Generic
    - Linux
    - Ubuntu
    - Ubuntu-13.04

Tracking a Mac specific file::

    $ homefiles --platform Darwin track ~/.mac-specific-file.txt
