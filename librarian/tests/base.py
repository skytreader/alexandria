import librarian
import unittest

librarian.init_blueprints()

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        try:
            librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE"])
        except:
            pass
        self.app = librarian.app.test_client()
