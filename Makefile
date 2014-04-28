clean:
	rm -rf build

builddir:
	mkdir -p build

build: builddir
	# just render all blogs. It's not expensive. Eventually, could choose to only
	# render updated blogs as long as template hasn't changed
	python render_blogs.py

	#sync static files
	rsync -az --delete template/css build/css
	rsync -az --delete template/CNAME build/CNAME
	rsync -az --delete template/images build/images
	rsync -az --delete template/static build/static
	rsync -az --delete template/index.html build/index.html
	rsync -az --delete template/favicon.ico build/favicon.ico

deploy:
	rsync -az --delete -e ssh --safe-links --exclude '.git' build/ ../llimllib.github.com/

	# execute the deploy commands in llimllib.github.com directory
	cd ../llimllib.github.com/ && \
		git add . && \
		git add -u && \
		git commit -m "updated on `date`" && \
		git push origin


.PHONY: clean builddir build deploy
