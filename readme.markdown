# Alexandria

[![Build Status](https://travis-ci.org/skytreader/alexandria.svg?branch=master)](https://travis-ci.org/skytreader/alexandria)
[![Coverage Status](https://coveralls.io/repos/skytreader/alexandria/badge.svg?branch=master&service=github)](https://coveralls.io/github/skytreader/alexandria?branch=master)

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

# Dev Set-up

Assuming you have a local mysql server accessbile by passwordless account
account `root`, create the relevant virtualenv and then,

    pip install -r requirements.txt
    fab create_database
    fab create_database:is_test=True
    python run.py

To load the fixture data,

    python fixtures.py

Note that, `run.py` must have ran _at least once_ before you load the fixture data.

# Testing Set-up

Assuming you have a local mysql database `alexandria_test` accessible by
passwordless account `root`, in the relevant virtualenv invoke `runtests`.

The test suite runner is ultimately, nose, but there are some envionment
variables that need to be set in order for tests to be successful. The script
takes care of that.

More relevant information can be found at `.travis.yml`.
