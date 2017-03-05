install:
	python3 setup.py install --user

test:
	nosetests tests

cover:
	nosetests tests --with-coverage --cover-package=pyne
