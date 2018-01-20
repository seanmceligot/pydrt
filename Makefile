.PHONY: test
test: check
	/usr/bin/pycodestyle tests/test_drt.py
	pytest -s

watch:
	when-changed -r drt make

watchtest:
	when-changed -r tests make

format:
	autopep8 -i drt/__init__.py
	/usr/bin/autopep8 -i tests/test_drt.py

init:
	pip install -r requirements.txt

.PHONY: check
check:
	pycodestyle drt/__init__.py
	MYPYPATH=/usr/lib/python3.6/site-packages/ mypy --ignore-missing-imports --follow-imports=skip --strict-optional  drt/ tests/
	#MYPYPATH=/usr/lib/python3.6/site-packages/ mypy --ignore-missing-imports  drt/ tests/

