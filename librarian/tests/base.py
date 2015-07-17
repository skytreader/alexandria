import librarian
import unittest

librarian.app.config["TESTING"] = True
librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])
librarian.init_blueprints()

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
