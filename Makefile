install: requirements
	pipenv install --three

test: install
	pipenv run tox -r

show-docs: install
	pipenv run tox -e docs
	cd dist/docs && python -m http.server

run: install
	@pipenv run python setup.py install
	pipenv run vmshepherd -c config/settings.example.yaml

requirements:
	@which pip3 &>/dev/null || (echo 'ERROR: Install python3 and pip3 (sudo apt-get install python3-pip)' && exit 1)
	@which pipenv || pip3 install --user pipenv -i https://pypi.python.org/pypi

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf dist build htmlcov .tox

.PHONY: install test show-docs run requirements clean
