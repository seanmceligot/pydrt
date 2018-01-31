.PHONY: test
ssh: check
	/usr/bin/pycodestyle tests/test_drt.py
	pytest -s -k ssh

test: check
	/usr/bin/pycodestyle tests/test_drt.py
	pytest -s

watch:
	#when-changed -r drt make
	while inotifywait -r -e close_write tests drt; do make test;done;

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
#MYPYPATH=/usr/lib/python3.6/site-packages/ mypy --ignore-missing-imports --follow-imports=skip --strict-optional  drt/ tests/
#MYPYPATH=/usr/lib/python3.6/site-packages/ mypy --follow-imports=skip drt/__init__.py
#MYPYPATH=/usr/lib/python3.6/site-packages/ mypy --follow-imports=skip tests/test_drt.py
#MYPYPATH=/usr/lib/python3.6/site-packages/  mypy --ignore-missing-imports drt/ tests/ | grep -v site-p
	MYPYPATH=/usr/lib/python3.6/site-packages/  mypy --follow-imports=skip --strict tests/test_drt.py  drt/__init__.py

