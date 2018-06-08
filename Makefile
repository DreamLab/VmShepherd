install: requirements
	( \
	  source env/bin/activate; \
	  sudo apt-get install -y graphviz libgraphviz-dev pkg-config; \
	  pip install -r test-requirements.txt; \
	  pip install -r requirements.txt; \
	)

test: install
	source env/bin/activate; \
	tox -r

show-docs: install
	source env/bin/activate; \
	tox -e docs
	cd dist/docs && python3 -m http.server

run: install
	source env/bin/activate; \
	python setup.py install; \
	vmshepherd -c config/settings.example.yaml;

requirements:
	@which virtualenv &>/dev/null || (echo 'ERROR: Install virtualenv.' && exit 1)
	@which python3 &>/dev/null || (echo 'ERROR: Install python 3.' && exit 1)
	@test -d env || virtualenv -p python3 env


clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf dist build htmlcov .tox

.PHONY: install test show-docs run requirements clean
