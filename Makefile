
version = 2.7
python = python$(version)

env: .venv/bin/python *.py *.cfg
	.venv/bin/pip install -r tools/reqs.txt --log /tmp/forest.pip.log

.venv/bin/python:
	virtualenv-$(version) --no-site-packages .venv

clean:
	@rm -rfv .venv/

rmpyc:
	@rm -rfv `find forest -name *.pyc`

.PHONY: env clean rmpyc
