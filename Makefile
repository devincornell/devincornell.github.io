all:
	python make.py
	git commit -a -m "compiling articles to html (automated commit)."
	git push
