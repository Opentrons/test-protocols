# test-protocols
Central location to catalog protocols used for testing.

## To use linting tools

- have python 3.10.*
- pip install pipenv
- pipenv install
- pipenv run black
- pipenv run isort
- pipenv run flake8

## TODO

- Create test to use opentrons https://pypi.org/project/opentrons/
  - Iterate over many of the protocols here and inspect the CLI output.
  - Make CRON github action
      - pulls edge built package
