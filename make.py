#!/usr/bin/env python

import sys

from os.path import join, isdir
from shutil import copy, rmtree
from shutil import rmtree

from lib.utils import copy_tree

def clean():
    if isdir("build"):
        rmtree("build")

def build():
    copy_tree(join("template", "960css"), join("build", "960css"))

def install():
    pass

if __name__ == "__main__":
    if sys.argv[-1] == "clean":
        clean()
    elif sys.argv[-1] == "build":
        build()
    elif sys.argv[-1] == "install":
        install()
    elif sys.argv[-1] == "pull":
        pull()
    else:
        clean()
        build()
        install()
