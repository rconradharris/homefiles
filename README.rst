=========
homefiles
=========


Features
========

    * Track files or directories
    * Easily clone files to another machine
    * Sync updates back to GitHub
    * OS bundles for OS-specific configurations
    * Custom bundles for machine-specific configurations


Getting Started
===============

Install::

    pip install homefiles


Track Your Files::

    homefiles init
    homefiles track ~/.vimrc


Sync Your Files To GitHub::

    homefiles sync 'Added vimrc'


Clone Your Files On Another Machine::

    homefiles clone rconradharris
    homefiles link


Bundles
=======

The data repo is composed of directories called 'bundles'. Each bundle
represents a set of files to be copied onto the target machine.

Bundles come in two flavors, OS-specific and custom. OS-specific bundles will
only be synced to machines that have a matching OS, for example Mac's will
sync ``OS-Darwin`` bundles whereas Ubuntu will sync ``Linux``, ``Ubuntu``, and
potentially ``Ubuntu-13.04`` bundles.

All machines will receive the ``Default`` bundle.

In addition, custom bundles can be defined which will be synced only when
directed to.


Bundle Layout
=============

Within the bundle, the layout is relative to your home directory, so
``Default/bin/foo.sh`` will be symlinked as ``$HOME/bin/foo.sh``.

Likewise, ``OS-Darwin/Documents/code/mac_only.sh`` will symlink to
``$HOME/Documents/code/mac_only.sh`` but only on Macs.

If a whole directory is being tracked, the ``.trackeddir`` marker file will be
present in it. This will cause the directory to be symlinked as a single unit,
rather than symlinking the individual files.


Repo Layout
===========
::

    .homefiles/
        Default/
            .vimrc
            bin/
                all_platforms.sh
        OS-Darwin/
            Documents/
                code/
                    mac_only.sh
                notes/
                    .trackeddir
        OS-Linux/
            bin/
                linux_only.sh
        OS-Ubuntu/
            bin/
                ubuntu_only.sh
        OS-Ubuntu-13.04/
            bin/
                raring_only.sh


Advanced
========


Determine available platforms for current machine::

    $ homefiles bundles
    - Default
    - OS-Darwin

    $ homefiles bundles
    - Default
    - OS-Linux
    - OS-Ubuntu
    - OS-Ubuntu-13.04

Tracking a Mac specific file::

    $ homefiles --bundle OS-Darwin track ~/.mac-specific-file.txt


Link using a custom bundles::

    $ homefiles --bundle=Laptop,Personal link
