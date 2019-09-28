.PHONY: all venv install-deps freeze db-create-default db-create-test db run lint flake8 pylint test coverage

all: lint coverage


venv:
	sudo apt-get -y install python-virtualenv python3-virtualenv
	virtualenv -p python3 venv

install-deps:
	pip install -r requirements.lock

freeze:
	@pip freeze | grep -v '^pkg-resources='


db-create-default:
	sudo -u postgres extra/database_create.sh fwe ${USER}

db-create-test:
	sudo -u postgres extra/database_create.sh fwe_test ${USER}

db:
	./fwe.sh dbremove
	./fwe.sh dbinit

run:
	FLASK_DEBUG=1 ./fwe.sh run --host 0.0.0.0 --port 19003


lint: flake8 pylint
flake8:
	python -m flake8 fwe tests
pylint:
	python -m pylint fwe tests

test:
	python -m pytest -v tests

coverage:
	coverage run --source fwe -m pytest tests -x -vv
	coverage report --show-missing --fail-under 100
