import os
from time import strptime, localtime
from distutils.file_util import copy_file, DistutilsFileError
from distutils.dir_util import mkpath

STAT_CACHE = {}

def cache(f):
    """Return the cached stat if it exists, otherwise, re-stat the file

    Use this instead of calling stat manually, to avoid extra file stats.

    Assumes files never change."""
    return STAT_CACHE.get(f, os.stat(f))

def parse_bloxsom(openfilehandle):
    lines = openfilehandle.readlines()

    #the first line is the title
    title = lines.pop(0).strip()

    #read metadata
    meta = {}
    while lines[0].startswith("#"):
        k, v = lines.pop(0).strip("#\n").split(" ", 1)
        meta[k] = v
        
    txt = "".join(lines)
    txt = highlight_code(txt, True)

    #TODO: pygmentize code snippets

    if 'time' in meta:
        time_tuple = strptime(meta['time'], "%m-%d-%y %H:%M")
    else:
        time_tuple = localtime(cache(f).st_mtime)

    return title, meta, time_tuple, txt

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

CODE_RE = re.compile("<code (?:\s*lang=(.*?))*>(.*?)<(?#)/code>", re.S)

def highlight_code(textstr, font_tags=False):
    for lang, code in CODE_RE.findall(textstr):
        if not lang: lang = "python"

        try:
            lexer = get_lexer_by_name(lang.strip('"'))
        except ClassNotFound:
            return
        formatter = HtmlFormatter(style="friendly", noclasses=font_tags)
        code = highlight(code, lexer, formatter)

        textstr = CODE_RE.sub(code, textstr, 1)
    return textstr
