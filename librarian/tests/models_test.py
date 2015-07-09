from factories import *
from librarian.errors import ConstraintError
from librarian.models import ISBN_START

import librarian
import unittest

class ModelsTest(unittest.TestCase):
    
    def setUp(self):
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_book(self):
        proper_book = BookFactory()

        with self.assertRaises(ConstraintError):
            BookFactory(publish_year = ISBN_START - 1)

    def tearDown(self):
        pass
