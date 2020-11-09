BLOG_ENTRIES=$(shell find -L blog_entries -iname '*.txt')

# for every %.txt file, we expect to generate a corresponding $(DEST)/%.html
DEST=build
BLOG_HTML=$(patsubst blog_entries/%.txt,$(DEST)/%.html,$(BLOG_ENTRIES))

TEMPLATES=$(shell find template -depth 1 -iname '*.html' -or -iname '*.mustache')
CSS=template/css/style.css

all: build

clean:
	rm -rf build

builddir:
	mkdir -p build

serve:
	modd # see modd.conf for details

prerequisites:
	pip install -r requirements.txt

build: prerequisites builddir $(TEMPLATES) $(CSS)
	# for now, just build all the blogs, it takes .5s
	python render_blog.py $(BLOG_ENTRIES)

	# then render the feeds
	python render_blog.py --feeds

	#sync static files
	rsync -az --delete template/css build
	rsync -az --delete template/CNAME build
	rsync -az --delete template/images build
	rsync -az --delete template/static build
	rsync -az --delete template/favicon.ico build
	rsync -az --delete template/index.html build

# This works, and I like it in theory since it lets us build only the blogs
# that changed, but it's very slow due to python startup time I think
#
# Regenerate all changed blog_entries
# $(DEST)/%.html: blog_entries/%.txt
# 	python render_blog.py $<

deploy:
	rsync -az --delete -e ssh --safe-links --exclude '.git' build/ billmill.org:/srv/billmill.org/


.PHONY: all clean builddir serve prerequisites build deploy
