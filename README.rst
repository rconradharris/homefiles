- Directory based layout (no manifest)
- Distinguish between OSes
- Symlink files or entire directories
	- __<dir> means create dir if it doesn't exist at destination
        - <dir> means symlink directory into repo

- homefiles script and data repo should be unified
- Repo should reside in ~/Documents/code/homefiles; override with .homefiles?

install.sh

./homefiles
	generic/
        .vimrc
        bin/
            vmrun

        Documents/
            notes/
                .trackeddir


    
- Start with generic/
- Prototype w/ python; decide whether to rewrite in sh



Homefiles2
==========


.homefiles remote repo for data
~/.homefiles for local repo

- clone|link|unlink|sync|track


homefiles clone rconradharris
homefiles track file
