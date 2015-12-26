#!/bin/bash

# To set up from clean install:

sudo apt-get update && sudo apt-get install python-pip git firefox xvfb && sudo pip install selenium flask flask-login flask-wtf flask-sqlalchemy xvfbwrapper && git clone http://github.com/aw31/Charon

config="\"\"\"Config file for Flask.\"\"\"
import os

_BASEDIR = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'YOUR_SECRET_KEY'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_BASEDIR, 'app.db')

CF_HANDLE = 'YOUR_USERNAME'
CF_PASSWORD = 'YOUR_PASSWORD'"

echo -e "$config" > Charon/config.py

# To run, first edit config.py, then execute "sudo python Charon/run.py".
