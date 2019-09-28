#!/bin/sh

export FLASK_APP=fwe:create_app
flask $@
