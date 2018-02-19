.PHONY: install
install: requirements
	pipenv install --three

.PHONY: test
test: install
	pipenv run tox -r

.PHONY: show-docs
show-docs: install
	pipenv run tox -e docs
	cd dist/docs && python -m http.server

.PHONY: run
run: install
	@pipenv run python setup.py install
	pipenv run vmshepherd -c config/settings.example.yaml

.PHONY: requirements
requirements:
	@which pip3 &>/dev/null || (echo 'ERROR: Install python3 and pip3 (sudo apt-get install python3-pip)' && exit 1)
	@which pipenv || pip3 install --user pipenv -i https://pypi.python.org/pypi
