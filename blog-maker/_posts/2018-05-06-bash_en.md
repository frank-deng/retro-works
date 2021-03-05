---
layout: post
title: Bash Shell Skills
tags: [Linux, Shell]
---


---

Execute GUI Programs
--------------------

Execute GUI programs in background mode from terminal, and suppresses stdout and stderr.

	(gui_program &>/dev/null &)

`gui_program` is the command you'd like to execute for the GUI program.

You can also add the following code to `~/.bash_aliases`:

	function xexec(){
		($@ &>/dev/null &)
	}
	complete -cf xexec

The use command `xexec gui_program arguments` to execute GUI programs in background mode from terminal with stdout and stderr suppressed.

---

Extract basename and extension
------------------------------

	BASENAME="${FILENAME%.*}";
	EXTENSION="${FILENAME##*.}";

---

Enumerate lines from stdin
--------------------------

	IFS=$'\n';
	for LINE in `ls`; do
		#Do some works on "${LINE}"
	done;

---

Enumerate command line arguments with space characters
------------------------------------------------------

	while [ -n "${1}" ]; do
		FILENAME="${1}";
		#Do some works on "${FILENAME}"
		shift 1;
	done;

---

Batch Renaming Using Perl's Rename Utility
------------------------------------------

Remove `.bak` extension:

	prename 's/\.bak$//' *

Convert filenames into lower case:

	prename 'y/A-Z/a-z/' *

Add prefix for `.txt` files:

	prename 's/(.*).txt$/prefix_$1.txt/' *.txt

On ArchLinux, you must install package `perl-rename` for this utility.

---

Find out text files with BOM header
-----------------------------------

Use `find` command and `file` command:

	find . -type f -exec file {} \; | grep BOM

Use `grep` command under bash shell:

	grep -rlI $'^\xEF\xBB\xBF' .
	
Exclude files with given extension (Useful to skip binary files and large files):

	grep -rlI $'^\xEF\xBB\xBF' --exclude=*.bin --exclude=*.dat .
	find . -type f -not \( -ipath '*.bin' -o -ipath '*.dat' \) -exec file {} \; | grep BOM
	
Exclude `.svn` directory:

	grep -rlI $'^\xEF\xBB\xBF' --exclude-dir=.svn .
	find . -type f -not \( -ipath '*.svn*' \) -exec file {} \; | grep BOM

---

Convert video into HTML5 compatible format
------------------------------------------

	ffmpeg -i INPUT_FILE -c:v libx264 -crf 18 -c:a aac -q:a 100 -strict experimental OUTPUT.mp4

---

Adjust Tab Size For VIM
-----------------------

Add the following lines to `/etc/vim/vimrc`:

	set tabstop=4
	set softtabstop=4
	set shiftwidth=4

---

Backup file with gzip compression and date suffix
-------------------------------------------------

	gzip -kS ".$(date '+%Y%m%d_%H%M').gz" backup_file

---

