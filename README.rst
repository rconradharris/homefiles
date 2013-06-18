=========
homefiles
=========


Features
========

    * Track files or directories
    * Easily clone files to another machine
    * Sync updates back to GitHub
    * Handles OS specific files


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
        Linux/
            bin/
                linux_only.sh
        Ubuntu/
            bin/
                ubuntu_only.sh
        Ubuntu-13.04/
            bin/
                raring_only.sh
