# Alexandria

[![Build Status](https://travis-ci.org/skytreader/alexandria.svg?branch=master)](https://travis-ci.org/skytreader/alexandria)
[![Coverage Status](https://coveralls.io/repos/skytreader/alexandria/badge.svg?branch=master&service=github)](https://coveralls.io/github/skytreader/alexandria?branch=master)

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

# Dev Set-up

## System packages

Install Docker and Docker Compose. Then, assuming you are in Ubuntu/Debian:

    sudo apt-get install -y mysql-client-5.7
    sudo apt-get install libmysqlclient-dev

You only need the MySQL client for some fabric commands. Otherwise just do,

    sudo docker-compose up

## Python set-up

Assuming you have successfully ran the Docker container, create a virtualenv and
do

    pip install -r requirements.txt
    fab create_database
    fab create_database:is_test=True
    python run.py

To load the fixture data,

    python fixtures.py

Note that, `run.py` must have ran _at least once_ before you load the fixture data.

# Testing Set-up

Assuming the Docker container is up, in the relevant virtualenv invoke `runtests`.

The test suite runner is ultimately, nose, but there are some envionment
variables that need to be set in order for tests to be successful. The script
takes care of that.

More relevant information can be found at `.travis.yml`.
