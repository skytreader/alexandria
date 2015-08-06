from base import AppTestCase
from faker import Faker
from flask.ext.login import login_user
from librarian.models import Book, Genre
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import (
  BookCompanyFactory, GenreFactory, LibrarianFactory
)

import factory
import flask.ext.login
import librarian
import unittest

fake = Faker()
fake.add_provider(BookFieldsProvider)

class ApiTests(AppTestCase):
    
    def setUp(self):
        super(ApiTests, self).setUp()
    
    def test_book_adder_happy(self):
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        login_user(_creator)

        isbn = fake.isbn()

        # Check that the book does not exist yet
        the_carpet_makers = librarian.db.session.query(Book).filter(Book.isbn == isbn).all()
        self.assertEquals(the_carpet_makers, [])

        single_author = {
            "isbn": isbn,
            "title": "The Carpet Makers",
            "genre": "io9",
            "authors": """[
                {
                    "last_name": "Eschenbach",
                    "first_name": "Andreas"
                }
            ]""",
            "illustrators": "[]",
            "editors": "[]",
            "translators": "[]",
            "publisher": "Scholastic",
            "printer": "UP Press",
            "year": "2013"
        }

        single_rv = self.client.post("/api/book_adder", data=single_author)

        self.assertEquals(single_rv._status_code, 200)
