from pub import task, file_rule
from glob import glob
from time import strftime
from codecs import open
from os.path import join, basename, isfile, isdir
from pystache import render
from functools import partial
from pub.shortcuts import rm, mkdir, rsync, newer, git, cd

from lib.utils import parse_bloxsom

@task
def clean():
    """Remove the build dir"""
    rm("-rf build")

def relative_url(f):
    return basename(f).replace("txt", "html")

def outname(f):
    return join("build", relative_url(f))

@task(private=True)
def make_build():
    if not isdir('build'): mkdir('build')

@file_rule("blog_entries/*.txt", outname)
def blog_entry(f):
    print "rendering: ", f

    title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))

    timestr = strftime('%b %d, %Y', time_tuple)

    blog_template = open(join("template", "blog_entry.mustache"), encoding="utf8").read()

    url = "http://billmill.org/%s" % relative_url(f)
    datelink = '<a href="%s">%s</a>' % (url, timestr)

    output = render(blog_template, {
        "title": title,
        "content": txt,
        "datelink": datelink
    })

    open(outname(f), "w", "utf8").write(output)

def regenerate_all():
    for f in glob("blog_entries/*.txt"): blog_entry(f)

@task("make_build", private=True)
def blog_template():
    """If any html file is older than the current template, regenerate all blogs"""
    for f in glob("build/*.html"):
        if newer(join("template", "blog_entry.mustache"), f):
            regenerate_all()
            break

def get_recent_entries(n):
    """return the n most recent blog posts"""
    entries = []
    for f in glob("blog_entries/*.txt"):
        url = basename(f[:-4] + '.html')
        title, meta, time_tuple, txt = parse_bloxsom(open(f, encoding="utf8"))
        entries.append((time_tuple, title, txt, url))

    #sort them by date descending
    return list(reversed(sorted(entries)))

def render_feed(template, timefmt):
    data = {
        "base_url": "http://billmill.org/",
        "blog_title": "My Name Rhymes",
        "blog_desc": "",
        "last_updated": "",
        "blog_author": "Bill Mill",
        "blog_email": "bill.mill@gmail.com",
        "blog_entries": []
    }

    entries = get_recent_entries(5)

    data["last_updated"] = strftime(timefmt, entries[0][0])

    #create the template dict
    for time, title, txt, url in entries[:5]:
        data["blog_entries"].append({
            "title": title,
            "link": "http://billmill.org/%s" % url,
            "time": strftime(timefmt, time),
            "desc": txt,
            "text": txt,
        })

    return render(template, data)


@task("make_build")
def rss():
    rss_template = open(join("template", "rss.mustache"), encoding="utf8").read()
    output = render_feed(rss_template, "%a, %d %b %Y %H:%M:%S +0000")

    open("build/Rss", "w", "utf8").write(output)


@task("make_build")
def atom():
    atom_template = open(join("template", "atom.mustache"), encoding="utf8").read()
    output = render_feed(atom_template, '%Y-%m-%dT%H:%M:%SZ')

    open("build/Atom", "w", "utf8").write(output)

@task("make_build", "blog_entry", "blog_template", "atom", "rss")
def build():
    t = partial(join, "template")
    b = partial(join, "build")

    #sync static files
    rsync("-az --delete %s %s" % (t("css/"),        b("css/")))
    rsync("-az --delete %s %s" % (t("CNAME"),       b("CNAME")))
    rsync("-az --delete %s %s" % (t("images/"),     b("images/")))
    rsync("-az --delete %s %s" % (t("static/"),     b("static/")))
    rsync("-az --delete %s %s" % (t("index.html"),  b("index.html")))
    rsync("-az --delete %s %s" % (t("favicon.ico"), b("favicon.ico")))

@task
def deploy():
    """deploy the site"""
    rsync("-az --delete -e ssh --safe-links --exclude '.git' build/ "
          "../llimllib.github.com/")
    cd("../llimllib.github.com")
    git("add .")
    git("add -u")
    git("commit -m 'updated on %s'" % strftime("%a, %d %b %Y %X"))
    git("push origin")
