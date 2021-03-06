.PHONY: test

c:
	autopep8 -i drt/create-ssh-connection.py
	pycodestyle drt/create-ssh-connection.py
	python3 drt/create-ssh-connection.py local password


test: check
	pycodestyle tests/test_drt.py
	pytest -s

ssh: check
	/usr/bin/pycodestyle tests/test_drt.py
	pytest -v -s -k ssh

watch:
	#when-changed -r drt make
	while inotifywait -r -e close_write tests drt; do make test;done;

watchtest:
	when-changed -r tests make

format:
	autopep8 -i drt/pssh.py
	autopep8 -i drt/__init__.py
	/usr/bin/autopep8 -i tests/test_drt.py

init:
	sudo pip install -r requirements.txt

.PHONY: check
check:
	pycodestyle drt/__init__.py
	pycodestyle drt/pssh.py
	MYPYPATH=/usr/lib/python3.6/site-packages/  mypy --ignore-missing-imports  --follow-imports=skip --strict drt/pssh.py tests/test_drt.py  drt/__init__.py

