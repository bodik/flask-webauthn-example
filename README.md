# Flask Webauthn Example

Simple Flask Webauthn example application


## Install

```
# prerequisities
apt-get install git sudo make postgresql-all wget gcc python3-dev

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
make install-extra
make test-extra

# run dev server
make db-create-default
make db
make run
```


## Webauthn.guide

### Registration

1. create credential
  - client retrieves publickKeyCredentialCreationOptions (pkcco) from server; state/challenge must be preserved on the server side
  - client/navigator calls authenticator with options to create credential
  - authenticator will create new credential and return an atestation response (new credential's public key + metadata)

2. register credential
  - attestation is packed; credential object is RO, ArrayBuffers must be casted to views (Uint8Array) before CBOR encoding
  - packed attestation is sent to the server for registration
  - server verifies the attestation and stores credential public key and association with the user
