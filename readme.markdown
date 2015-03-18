# Alexandria

Citing related repos compels me to mention [this one](https://github.com/skytreader/Librarian).

# Dev Set-up

Assuming you have a local mysql database `alexandria` accessbile by passwordles
account `root`, create the relevant virtualenv and then,

    pip install -r requirements.txt
    python run.py

To load the fixture data,

    python fixtures.py

Note that, `run.py` must have ran _at least once_ before you load the fixture data.
