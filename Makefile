
version = 2.7
python = python$(version)

build: .venv/bin/python .pip.log *.py *.cfg
	.venv/bin/python setup.py develop

.pip.log: .venv/bin/python tools/reqs.txt
	.venv/bin/pip install -r tools/reqs.txt --log .pip.log

.venv/bin/python:
	virtualenv-$(version) --no-site-packages .venv

clean:
	@rm -rfv .venv/

rmpyc:
	@rm -rfv `find forest -name *.pyc`


.PHONY: build clean rmpyc
