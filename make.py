#!/usr/bin/env python

import sys

from os import mkdir, unlink, stat
from glob import glob
from time import strftime, mktime
from shutil import copy, rmtree
from codecs import open
from os.path import join, isdir, isfile, basename
from datetime import datetime

from pystache import render

from lib.utils import copy_tree, parse_bloxsom

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

    most_recent = []
    for f in glob("blog_entries/*.txt"):
        title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))

        timestr = strftime('%b %d, %Y', time_tuple)

        relative_url = basename(f).replace("txt", "html")
        output_filename = join("build", relative_url)

        url = "http://billmill.org/%s" % relative_url
        datelink = '<a href="%s">%s</a>' % (url, timestr)

        output = render(blog_template, {
            "title": title,
            "content": txt,
            "datelink": datelink
        })

        open(output_filename, "w", "utf8").write(output)

        most_recent.append((mktime(time_tuple), {
            "title": title,
            "url": url,
            "rfc822date": strftime("%a, %d %b %Y %H:%M:%S +0000", time_tuple),
            "isodate": datetime.fromtimestamp(mktime(time_tuple)).isoformat(),
            "summary": txt,
            "relative_url": relative_url,
        }))

    most_recent.sort(reverse=True)

    #output RSS
    rss_output = render(open(t("rss.mustache")).read(), {
        "items": [data for date, data in most_recent[:5]]
    })
    open("build/Rss", "w").write(rss_output)
    
    #output atom
    atom_output = render(open(t("atom.mustache")).read(), {
        "items": [data for date, data in most_recent[:5]],
        "most_recent_update": most_recent[0][1]["isodate"]
    })
    open("build/Atom", "w").write(rss_output)

if __name__ == "__main__":
    if sys.argv[-1] == "clean":
        clean()
    elif sys.argv[-1] == "build":
        build()
    elif sys.argv[-1] == "pull":
        pull()
    else:
        clean()
        build()
