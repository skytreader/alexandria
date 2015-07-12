from faker import Faker
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookCompanyFactory, GenreFactory

import librarian
import unittest

fake = Faker()
fake.add_provider(BookFieldsProvider)

class ApiTests(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
        librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])

    def test_book_adder(self):
        genre_record = GenreFactory()
        publisher_record = BookCompanyFactory()
        printer_record = BookCompanyFactory()

        single_author = {
            "isbn": fake.isbn(),
            "title": "The Carpet Makers",
            "genre": genre_record.genre_name,
            "authors": """[
                {
                    "last_name": "Eschenbach",
                    "first_name": "Andreas"
                }
            ]""",
            "illustrators": "[]",
            "editors": "[]",
            "translators": "[]",
            "publisher": publisher_record.company_name,
            "printer": printer_record.company_name,
            "year": "2013"
        }

        single_rv = self.app.post("/api/book_adder", data=single_author)

        self.assertEquals(single_rv._status_code, 200)
