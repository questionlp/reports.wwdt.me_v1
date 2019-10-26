#!/bin/sh
# Shell script used to start up Flask for local development and testing
export FLASK_ENV=local
. venv/bin/activate
venv/bin/python3 app.py 