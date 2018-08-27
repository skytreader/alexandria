# Alexandria

[![Build Status](https://travis-ci.org/skytreader/alexandria.svg?branch=master)](https://travis-ci.org/skytreader/alexandria)
[![Coverage Status](https://coveralls.io/repos/skytreader/alexandria/badge.svg?branch=master&service=github)](https://coveralls.io/github/skytreader/alexandria?branch=master)

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

# Dev Set-up

Install `docker` and `docker-compose` and do `docker-compose up --build`.

Note that at this point, you don't have fixture data yet. So do

    docker-compose run --entrypoing "python fixtures.py" web

# Testing Set-up

Assuming you have a local mysql database `alexandria_test` accessible by
passwordless account `root`, in the relevant virtualenv invoke `runtests`.

The test suite runner is ultimately, nose, but there are some envionment
variables that need to be set in order for tests to be successful. The script
takes care of that.

More relevant information can be found at `.travis.yml`.

# Documentation

## JavaScript

Assuming `npm` is installed, use jsdoc.

    $ npm install jsdoc
    $ node_modules/jsdoc/jsdoc.js -r librarian/static/scripts/

You can then find the docs in the `/out` directory of the project's root.
