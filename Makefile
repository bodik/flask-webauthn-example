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
runssl:
	FLASK_DEBUG=1 ./fwe.sh run --host 0.0.0.0 --port 19003 --cert server.crt --key server.key


lint: flake8 pylint
flake8:
	python -m flake8 fwe tests
pylint:
	python -m pylint fwe tests

test:
	python -m pytest -v tests/app

coverage:
	coverage run --source fwe -m pytest tests/app -x -vv
	coverage report --show-missing --fail-under 100


install-extra: /usr/local/bin/geckodriver
	which firefox || sudo apt-get -y install firefox-esr

/usr/local/bin/geckodriver:
	rm -f /tmp/geckodriver.tar.gz
	wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
	sudo tar xzf /tmp/geckodriver.tar.gz -C /usr/local/bin geckodriver

test-extra:
	python -m pytest -x -vv tests/selenium
