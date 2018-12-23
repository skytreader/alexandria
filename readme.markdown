# Alexandria

[![Build Status](https://travis-ci.org/skytreader/alexandria.svg?branch=master)](https://travis-ci.org/skytreader/alexandria)
[![codecov](https://codecov.io/gh/skytreader/alexandria/branch/master/graph/badge.svg)](https://codecov.io/gh/skytreader/alexandria)

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

## Dev Set-up

Install `docker` and `docker-compose` and do `docker-compose up --build`.

Create a virtualenv and do `pip install -r requirements.txt`. Note that this
virtualenv is not required if you just want to run Alexandria; it is needed for
[invoke](http://www.pyinvoke.org/) and is mainly for development and
administration.

Note that at this point, you don't have fixture data yet. So do

    invoke load_fixtures

Or, if you already have a database dump you want to load into the app,

    invoke load-db [--dump-name dump.sql]

In general, have a look at `tasks.py` (or just `invoke -l`) for a bunch of
useful routines.

## Testing Set-up

To run unit tests just do,

    docker-compose -f docker-compose-test.yml run test ./dockertests

More relevant information can be found at `.travis.yml`.

## Documentation

### JavaScript

Assuming `npm` is installed, use jsdoc.

    $ npm install jsdoc
    $ node_modules/jsdoc/jsdoc.js -r librarian/static/scripts/

You can then find the docs in the `/out` directory of the project's root.
