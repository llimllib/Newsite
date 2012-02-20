#!/usr/bin/env python

import sys

from os import mkdir, unlink, stat
from glob import glob
from time import strptime, strftime, mktime, localtime
from shutil import copy, rmtree
from codecs import open
from os.path import join, isdir, isfile, basename

from pystache import render

from lib.utils import copy_tree

def clean():
    if isdir("build"):
        rmtree("build")

    if isfile("build"):
        unlink("build")

def build():
    def t(dir_): return join("template", dir_)

    mkdir("build")

    for dir_ in ("css", "images"):
        copy_tree(t(dir_), join("build", dir_))
    
    copy(t("index.html"), "build/")

    blog_template = open(t("blog_entry.mustache")).read()

    for f in glob("blog_entries/*.txt"):
        lines = open(f, encoding="utf8").readlines()

        #the first line is the title
        title = lines.pop(0).strip()

        #read metadata
        meta = {}
        while lines[0].startswith("#"):
            k, v = lines.pop(0).strip("#\n").split(" ", 1)
            meta[k] = v
            
        txt = "".join(lines)

        if 'time' in meta:
            time_tuple = strptime(meta['time'], "%m-%d-%y %H:%M")
        else:
            time_tuple = localtime(stat(f)[8])

        timestr = strftime('%b %d, %Y', time_tuple)

        newname = basename(f).replace("txt", "html")
        output_filename = join("build", newname)

        datelink = '<a href="http://billmill.org/%s">%s</a>' % (newname, timestr)

        output = render(blog_template, {
            "title": title,
            "content": txt,
            "datelink": datelink
        })

        open(output_filename, "w", "utf8").write(output)

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
