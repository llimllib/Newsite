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

@task("make_build", "blog_entry", "blog_template")
def build():
    t = partial(join, "template")
    b = partial(join, "build")

    #sync static files
    rsync("-az --delete %s %s" % (t("css/"),        b("css/")))
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
    git("commit -m \"updated on %s\"" % strftime("%a, %d %b %Y %X"))
    git("push origin")
