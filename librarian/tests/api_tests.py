from base import AppTestCase
from faker import Faker
from librarian.models import Book
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookCompanyFactory, GenreFactory

import librarian
import unittest

fake = Faker()
fake.add_provider(BookFieldsProvider)

class ApiTests(AppTestCase):
    
    def setUp(self):
        super(ApiTests, self).setUp()
    
    def test_book_adder_happy(self):
        genre_record = GenreFactory()
        publisher_record = BookCompanyFactory()
        printer_record = BookCompanyFactory()
        librarian.db.session.commit()
        isbn = fake.isbn()

        # Check that the book does not exist yet
        the_carpet_makers = librarian.db.session.query(Book).filter(Book.isbn == isbn).all()
        self.assertEquals(the_carpet_makers, [])

        single_author = {
            "isbn": isbn,
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
        the_carpet_makers = librarian.db.session.query(Book).filter(Book.isbn == isbn).first()
        self.assertEquals(isbn, the_carpet_makers.isbn)
        self.assertEquals("The Carpet Makers", the_carpet_makers.title)
        self.assertEquals(genre_record.record_id, the_carpet_makers.genre)
