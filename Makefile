DIRS=Theme1-ParcoursDeGraphes/exercices Theme1-ParcoursDeGraphes/notes
Documents=$(foreach dir, $(DIRS), $(wildcard $(dir)/*.ipynb $(dir)/*.py $(dir)/*.txt $(dir)/*/*.txt $(dir)/*.png $(dir)/*.jpeg))

build: $(Documents:%=_build/%)

install: build
	rsync -avz --exclude __pycache__ --exclude '*flymake*' --exclude '.ipynb*' --exclude '*~' --delete _build/ cocalc-algo:2018-19

_build/%: %
	mkdir -p `dirname $@`
	ln -f $< $@

_build/%.py: %.py
	mkdir -p `dirname $@`
	python2 bin/strip-code $< > $@

_build/%.ipynb: %.ipynb
	mkdir -p `dirname $@`
	nbgrader assign `dirname $*` --create --force --notebook=`basename $*`
#	python2 bin/strip-notebook $< > $@
