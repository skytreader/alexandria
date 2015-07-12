from factories import *
from librarian.errors import ConstraintError
from librarian.models import ISBN_START

import librarian
import unittest

class ModelsTest(unittest.TestCase):
    
    def setUp(self):
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_book_errors(self):
        with self.assertRaises(ConstraintError):
            BookFactory(publish_year = ISBN_START - 1)

        with self.assertRaises(ConstraintError):
            # This is an invalid ISBN. It should be 978-3-16-148410-0
            BookFactory(isbn="9783161484105")

    def tearDown(self):
        pass
