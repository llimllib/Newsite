#!/usr/bin/env python

import argparse
from codecs import open
from glob import glob
from lib.utils import parse_bloxsom
from os.path import join, basename
from pystache import render
from time import strftime


def relative_url(f):
    return basename(f).replace("txt", "html")


def outname(f):
    return join("build", relative_url(f))


def render_posts(posts):
    blog_template = open(
        join("template", "blog_entry.mustache"), encoding="utf8"
    ).read()

    for f in posts:
        title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))

        timestr = strftime("%b %d, %Y", time_tuple)

        url = "http://billmill.org/%s" % relative_url(f)
        datelink = '<a href="%s">%s</a>' % (url, timestr)

        output = render(
            blog_template, {"title": title, "content": txt, "datelink": datelink}
        )

        open(outname(f), "w", "utf8").write(output)


def get_recent_entries(n):
    """return the n most recent blog posts"""
    entries = []
    for f in glob("blog_entries/*.txt"):
        url = basename(f[:-4] + ".html")
        title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))
        entries.append((time_tuple, title, txt, url))

    # sort them by date descending
    return list(reversed(sorted(entries)))


def render_feed(template, timefmt):
    data = {
        "base_url": "http://billmill.org/",
        "blog_title": "My Name Rhymes",
        "blog_desc": "",
        "last_updated": "",
        "blog_author": "Bill Mill",
        "blog_email": "bill.mill@gmail.com",
        "blog_entries": [],
    }

    entries = get_recent_entries(5)

    data["last_updated"] = strftime(timefmt, entries[0][0])

    # create the template dict
    for time, title, txt, url in entries[:5]:
        data["blog_entries"].append(
            {
                "title": title,
                "link": "http://billmill.org/%s" % url,
                "time": strftime(timefmt, time),
                "desc": txt,
                "text": txt,
            }
        )

    return render(template, data)


def render_feeds():
    rss_template = open(join("template", "rss.mustache"), encoding="utf8").read()
    output = render_feed(rss_template, "%a, %d %b %Y %H:%M:%S +0000")

    open("build/Rss", "w", "utf8").write(output)

    atom_template = open(join("template", "atom.mustache"), encoding="utf8").read()
    output = render_feed(atom_template, "%Y-%m-%dT%H:%M:%SZ")

    open("build/Atom", "w", "utf8").write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render some blog entries")
    parser.add_argument(
        "files",
        metavar="files",
        type=str,
        nargs="*",
        help="files to render. Ignored if --feeds is passed",
    )
    parser.add_argument(
        "--feeds", action="store_const", const=True, help="render feeds not blogs"
    )
    args = parser.parse_args()

    if args.feeds:
        render_feeds()
    else:
        render_posts(args.files)
