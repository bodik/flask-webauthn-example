# Flask Webauthn Example

Simple Flask Webauthn example application


## Install

```
# prerequisities
apt-get install git sudo make postgresql-all

# clone from repository
git clone https://github.com/bodik/flask-webauthn-example /opt/fwe
cd /opt/fwe
ln -s ../../extra/git_hookprecommit.sh .git/hooks/pre-commit

# create and activate virtualenv
make venv
. venv/bin/activate

# install dependencies
make install-deps

# run tests
make db-create-test
make test
make coverage

# run dev server
make db-create-default
make db
make run
```
