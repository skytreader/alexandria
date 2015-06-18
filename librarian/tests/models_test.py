import os
import librarian
import unittest
import tempfile

class ModelsTest(unittest.TestCase):
    
    def setUp(self):
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_shallow(self):
        self.assertTrue(True)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
