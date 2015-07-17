import librarian
import unittest

librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])
librarian.init_blueprints()

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
