.PHONY: black
black:
	pipenv run python -m black **/*.py

.PHONY: flake8
flake8:
	pipenv run python -m flake8 **/*.py

.PHONY: isort
isort:
	pipenv run python -m isort ./

.PHONY: lint
lint:
	$(MAKE) black
	$(MAKE) isort

.PHONY: setup
setup:
	pipenv install

.PHONY: teardown
teardown:
	pipenv --rm
