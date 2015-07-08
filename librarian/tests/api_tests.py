import librarian
import unittest

class ApiTests(unittest.TestCase):
    
    def setUp(self):
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_book_adder(self):
        single_everything = {
        
        }
