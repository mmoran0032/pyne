install:
	python3 setup.py install --user

test:
	py.test --cov-report term --cov=pyne
