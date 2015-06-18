import os
import app
import unittest
import tempfile

class ModelsTest(unittest.TestCase):
    
    def setUp(self):
        app.app.init_db(app.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_shallow(self):
        self.assertTrue(True)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
