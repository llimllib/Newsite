#!/usr/bin/env python

import argparse
from glob import glob
from os.path import join, basename
from time import strftime, struct_time
from typing import List, Any, Dict, Tuple

from lib.utils import parse_bloxsom
from pystache import render


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

        if "draft" in meta:
            print(f"Not publishing draft: {title}")
            continue

        timestr = strftime("%b %d, %Y", time_tuple)

        datelink = f'<a href="{relative_url(f)}">{timestr}</a>'

        output = render(
            blog_template, {"title": title, "content": txt, "datelink": datelink}
        )

        open(outname(f), "w", encoding="utf8").write(output)


# time, title, content, url, metadata
Entry = Tuple[struct_time, str, str, str, Dict[str, str]]


# XXX: this is getting entries out of order I think, US map for the web is
# showing as newer than US State choropleth
def get_recent_entries(n: int) -> List[Entry]:
    """return the n most recent blog posts"""
    entries = []
    for f in glob("blog_entries/*.txt"):
        url = basename(f[:-4] + ".html")
        title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))
        entries.append((time_tuple, title, txt, url, meta))

    # sort them by date descending
    return list(reversed(sorted(entries)))[:n]


def render_feed(template: str, timefmt: str, entries: List[Entry]) -> str:
    data = {
        "base_url": "http://billmill.org/",
        "blog_title": "My Name Rhymes",
        "blog_desc": "",
        "last_updated": "",
        "blog_author": "Bill Mill",
        "blog_email": "bill.mill@gmail.com",
        "blog_entries": [],
    }

    data["last_updated"] = strftime(timefmt, entries[0][0])

    # create the template dict
    for time, title, txt, url, _ in entries:
        data["blog_entries"].append(
            {
                "title": title,
                "link": "https://billmill.org/%s" % url,
                "time": strftime(timefmt, time),
                "desc": txt,
                "text": txt,
            }
        )

    return render(template, data)


def render_index(entries: List[Any]) -> None:
    index_template = open(join("template", "index.html"), encoding="utf8").read()
    data = {"blog_entries": []}
    for time, title, txt, url, _ in entries:
        data["blog_entries"].append(
            {
                "title": title,
                "link": url,
                "time": strftime("%m %d, %Y", time),
                "desc": txt,
                "text": txt,
            }
        )
    open("build/index.html", "w", encoding="utf8").write(render(index_template, data))


def render_feeds(entries: List[Entry]) -> None:
    rss_template = open(join("template", "rss.mustache"), encoding="utf8").read()
    output = render_feed(rss_template, "%a, %d %b %Y %H:%M:%S +0000", entries)

    open("build/Rss", "w", encoding="utf8").write(output)

    atom_template = open(join("template", "atom.mustache"), encoding="utf8").read()
    output = render_feed(atom_template, "%Y-%m-%dT%H:%M:%SZ", entries)

    open("build/Atom", "w", encoding="utf8").write(output)


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
        render_feeds(get_recent_entries(10))
    else:
        render_posts(args.files)
        render_index(get_recent_entries(10))
