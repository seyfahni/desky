
SHELL := /bin/bash

IN_VENV := { [[ -n "$${VIRTUAL_ENV+x}" ]] || source venv/bin/activate ; } &&

run : init
	@${IN_VENV} python -m desky

test : init
	@${IN_VENV} python -m unittest

init : venv requirements.txt
	@${IN_VENV} python -m pip install -qr requirements.txt

freeze : venv
	@${IN_VENV} python -m pip freeze >requirements.txt

venv :
	python -m venv venv
	${IN_VENV} pip install --upgrade pip

.PHONY: run test init
