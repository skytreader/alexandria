# Alexandria

[![Build Status](https://travis-ci.org/skytreader/alexandria.svg?branch=master)](https://travis-ci.org/skytreader/alexandria)
[![Coverage Status](https://coveralls.io/repos/skytreader/alexandria/badge.svg?branch=master&service=github)](https://coveralls.io/github/skytreader/alexandria?branch=master)

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

# Dev Set-up

If, for some reason, the following installs cannot be done (you might not have
sudo permissions, or maybe mysql is messing around), you may attempt to set-up
with Docker as shown in a section below.

## System packages

Assuming you are in Ubuntu/Debian:

    sudo apt-get install -y mysql-server-5.7
    sudo apt-get install -y mysql-client-core-5.7
    sudo apt-get install -y mysql-client-5.7
    sudo apt-get install libmysqlclient-dev

## Python set-up

Assuming you have a local mysql server accessbile by passwordless account
account `root`, create the relevant virtualenv and then,

    pip install -r requirements.txt
    fab create_database
    fab create_database:is_test=True
    export ALEXANDRIA_CONFIG='../config.py'
    python run.py

To load the fixture data,

    python fixtures.py

Note that, `run.py` must have ran _at least once_ before you load the fixture data.

## Docker set-up

**Note:** Docker will not always be maintained. Maybe, at most officially, for
Travis CI builds. But other than that, there will be no guarantees. Almost
certainly, some, if not most, Fabric commands will not work with Docker.

Simply install `docker` and `docker-compose` and do `docker-compose up --build`.
When running the app from a docker set-up, set the `ALEXANDRIA_CONFIG` env var
to `../docker_config.py`. That is,

    export ALEXANDRIA_CONFIG='../docker_config.py'

# Testing Set-up

Assuming you have a local mysql database `alexandria_test` accessible by
passwordless account `root`, in the relevant virtualenv invoke `runtests`.

The test suite runner is ultimately, nose, but there are some envionment
variables that need to be set in order for tests to be successful. The script
takes care of that.

More relevant information can be found at `.travis.yml`.
