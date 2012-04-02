import os, shutil
from time import strptime, localtime
from distutils.file_util import copy_file, DistutilsFileError
from distutils.dir_util import mkpath

STAT_CACHE = {}

def cache(f):
    """Return the cached stat if it exists, otherwise, re-stat the file

    Use this instead of calling stat manually, to avoid extra file stats.

    Assumes files never change."""
    return STAT_CACHE.get(f, os.stat(f))

def copy_tree(src, dst, ignores=()):
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.
    
    Ignore any file whose name is in the "ignores" iterable.

    This is a forked version of distutils.dir_util.copy_tree, which
    did not have a way to ignore the files I wanted to ignore.
    """
    if not os.path.isdir(src):
        raise DistutilsFileError, "cannot copy tree '%s': not a directory" % src

    try:
        names = os.listdir(src)
    except os.error, (errno, errstr):
        raise DistutilsFileError, "error listing files in '%s': %s" % (src, errstr)

    mkpath(dst)

    outputs = []

    for n in names:
        if n in ignores: continue

        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

#def copy_tree(src, dst, preserve_mode=1, preserve_times=1,
#              preserve_symlinks=0, update=0, verbose=1, dry_run=0):

        if os.path.islink(src_name):
            continue
        elif os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name, ignores))
        else:
            copy_file(src_name, dst_name, verbose=1)
            outputs.append(dst_name)

    return outputs

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
