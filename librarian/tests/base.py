import librarian
import unittest

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
        try:
            librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE"])
        except:
            pass
