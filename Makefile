
version = 2.7
python = python$(version)

env: .venv/bin/python *.py *.cfg
	.venv/bin/pip install -r tools/reqs.txt --log /tmp/forest.pip.log

.venv/bin/python:
	virtualenv-$(version) --no-site-packages .venv
	@touch $@

test: .venv/bin/py.test
	.venv/bin/py.test -q -n4

.venv/bin/py.test: setup.py setup.cfg
	.venv/bin/python setup.py dev
	@touch $@

clean:
	@rm -rfv .venv/

rmpyc:
	@rm -rfv `find forest -name *.pyc`

.PHONY: env clean rmpyc test
