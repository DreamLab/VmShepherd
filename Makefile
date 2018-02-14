install: requirements
	pipenv install --three

test: install
	pipenv run tox -r

run: install
	@pipenv run python setup.py install
	pipenv run vmshepherd -c config/settings.example.yaml

requirements:
	@which pip3 &>/dev/null || (echo 'ERROR: Install python3 and pip3 (sudo apt-get install python3-pip)' && exit 1)
	@which pipenv || pip3 install --user pipenv -i https://pypi.python.org/pypi

.PHONY: test requirements install run
