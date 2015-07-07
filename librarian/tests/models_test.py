import librarian
import unittest

class ModelsTest(unittest.TestCase):
    
    def setUp(self):
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_shallow(self):
        self.assertTrue(True)

    def tearDown(self):
        pass
