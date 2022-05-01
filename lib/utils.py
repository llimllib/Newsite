import os
import re
from time import strptime, localtime

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


STAT_CACHE = {}


def cache(f):
    """Return the cached stat if it exists, otherwise, re-stat the file

    Use this instead of calling stat manually, to avoid extra file stats.

    Assumes files never change."""
    return STAT_CACHE.get(f, os.stat(f))


def parse_bloxsom(openfilehandle):
    lines = openfilehandle.readlines()

    # the first line is the title
    title = lines.pop(0).strip()

    # read metadata
    meta = {}
    while lines[0].startswith("#"):
        k, v = lines.pop(0).strip("#\n").split(" ", 1)
        meta[k] = v

    txt = "".join(lines)
    txt = highlight_code(txt, True)

    if "time" in meta:
        time_tuple = strptime(meta["time"], "%m-%d-%y %H:%M")
    else:
        time_tuple = localtime(cache(openfilehandle.name).st_mtime)

    return title, meta, time_tuple, txt


# CODE_RE = re.compile(r"<code[^>]*(?:lang=(.*?))*>(.*?)<(?#)/code>", re.S)
CODE_RE = re.compile(r"<code(.*?)>(.*?)</code>", re.S)


def highlight_code(textstr, font_tags=False):
    for attr_string, code in CODE_RE.findall(textstr):
        # attrs is a string like ' class="inline" lang="python"'; split it by
        # spaces then by equals, strip quotes, and turn it into a dictionary
        attrs = {}
        if attr_string.strip():
            attrs = dict(
                map(lambda z: z.strip('"'), y.split("=")) for y in attr_string.split()
            )

        try:
            lexer = get_lexer_by_name(attrs.get("lang", "python"))
        except ClassNotFound:
            return

        # add the inline class if present
        if "class" in attrs and "inline" in attrs["class"].split():
            formatter = HtmlFormatter(style="xcode", noclasses=font_tags, nowrap=True)
            code = highlight(code, lexer, formatter)
            code = code.replace("span", 'span class="highlight inline"', 1)
        else:
            formatter = HtmlFormatter(style="xcode", noclasses=font_tags)
            code = highlight(code, lexer, formatter)

        # make code a lambda so it doesn't process slashes:
        #
        # repl can be either a string or a callable;
        # if a string, backslash escapes in it are processed.  If it is
        # a callable, it's passed the Match object and must return
        # a replacement string to be used.
        textstr = CODE_RE.sub(lambda _: code, textstr, 1)
    return textstr
