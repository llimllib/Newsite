BLOG_ENTRIES=$(shell find -L blog_entries -iname '*.txt')

# for every %.txt file, we expect to generate a corresponding $(DEST)/%.html
DEST=build
BLOG_HTML=$(patsubst blog_entries/%.txt,$(DEST)/%.html,$(BLOG_ENTRIES))

TEMPLATES=$(shell find template -depth 1 -iname '*.html' -or -iname '*.mustache')
CSS=template/css/style.css

all: build

requirements:
	pip install -r requirements.py

clean:
	rm -rf build

builddir:
	mkdir -p build

serve:
	modd # see modd.conf for details

prerequisites:
	pip install -r requirements.txt

build: prerequisites builddir $(TEMPLATES) $(CSS)
	# render all the blog entries - I'd like to do just the ones that need to
	# be built but I haven't yet figured out how to express that
	python render_blog.py $(BLOG_ENTRIES)

	# then render the feeds
	python render_blog.py --feeds

	#sync static files
	rsync -az --delete template/css build
	rsync -az --delete template/CNAME build
	rsync -az --delete template/images build
	rsync -az --delete template/static build
	rsync -az --delete template/favicon.ico build
	rsync -az --delete template/reassess build

# We use the .blog_html file to track when we last rendered any blogs. Any
# blog entry (*.txt) file newer than this file will get rebuilt into HTML
# I'm not sure if there's any way to do this without an extra file?
#
# This has a problem though: if we update a template file, all blog entries
# need to be rebuilt, but they also can't go in the argument list for
# render_blog.py
#
# for now I'm going to leave this here but not use it
.blog_html: $(BLOG_ENTRIES)
	python render_blog.py $$(grep *.txt $?)
	touch .blog_html

deploy:
	rsync -az --delete -e "ssh -i $$HOME/.ssh/billmill.org.key" --safe-links --exclude '.git' build/ root@billmill.org:/var/www/html/

# sync the cdn dir to the static bucket on my cdn
cdn: listing
	s3cmd sync --acl-public cdn/ s3://llimllib/static/

# flush the digital ocean CDN
flush:
	doctl compute cdn flush \
		$$(doctl compute cdn list --format ID | tail -n1) \
		--files *

# generate a listing of the files in the gifs directory
listing:
	cd cdn/gifs && \
	tree -H '.' \
    -L 1 \
    --noreport \
    --charset utf-8 \
    --ignore-case \
    -I "index.html" \
    -h -s -D \
    -o index.html

.PHONY: all clean builddir listing serve prerequisites build deploy cdn flush
