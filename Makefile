
SHELL := /bin/bash

IN_VENV := { [[ -n "$${VIRTUAL_ENV+x}" ]] || source venv/bin/activate ; } &&

run : init
	${IN_VENV} python desky

init : venv requirements.txt
	${IN_VENV} pip install -r requirements.txt

venv :
	python -m venv venv
	${IN_VENV} pip install --upgrade pip

test :
	py.test tests

.PHONY: init test
