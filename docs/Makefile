PYTHON ?= python

build:
	$(PYTHON) tools/create_function_table.py
	jb build --all -v .

upload:	build
	ghp-import -n -p -f _build/html

clean:
	rm -rf _build

view:
	open _build/html/index.html
