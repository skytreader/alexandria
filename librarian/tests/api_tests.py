from base import AppTestCase
from faker import Faker
from flask.ext.login import login_user
from librarian.models import Book, BookCompany, BookParticipant, BookPerson, Genre
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import (
  BookCompanyFactory, GenreFactory, LibrarianFactory
)

import factory
import flask.ext.login
import json
import librarian
import re
import string
import unittest

fake = Faker()
fake.add_provider(BookFieldsProvider)

PROLLY_ROMAN_NUM = re.compile("^[%s]$" % (string.uppercase))

class ApiTests(AppTestCase):
    
    def setUp(self):
        super(ApiTests, self).setUp()
    
    def test_book_adder_happy(self):
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(BookPerson, lastname="Eschenbach",
          firstname="Andreas")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")

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

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(BookPerson, lastname="Eschenbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

    def test_multiple_book_people(self):
        """
        Test adding multiple people for the fields where person names are
        expected. We can assume that records are "fresh".
        """

        def make_name_object():
            name = fake.name().split()
            is_roman_num = PROLLY_ROMAN_NUM.match(name[-1])
            last_name = " ".join(name[-1:]) if is_roman_num else name[-1]
            first_name = name[0]

            return {"first_name": first_name, "last_name": last_name}

        def verify_bookperson_inserted(persons, role, bookid):
            for p in persons:
                _p = self.verify_inserted(BookPerson, firstname=p["first_name"],
                  lastname=p["last_name"])
                self.verify_inserted(BookParticipant, person_id=_p.id,
                  role_id=self.ROLE_IDS[role], book_id=bookid)

        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()
        title = fake.title()

        authors = [make_name_object() for _ in range(4)]
        illustrators = [make_name_object() for _ in range(4)]
        editors = [make_name_object() for _ in range(4)]
        translators = [make_name_object() for _ in range(4)]

        req_data = {
            "isbn": isbn,
            "title": title,
            "genre": "Multinational",
            "authors": json.dumps(authors),
            "illustrators": json.dumps(illustrators),
            "editors": json.dumps(editors),
            "translators": json.dumps(translators),
            "publisher": "Scholastic",
            "printer": "UP Press",
            "year": "2013"
        }

        req_val = self.client.post("/api/book_adder", data=req_data)
        self.assertEqual(200, req_val.status_code)
        created_book = (librarian.db.session.query(Book)
          .filter(Book.isbn==isbn).first())
        
        verify_bookperson_inserted(authors, "Author", created_book.id)
        verify_bookperson_inserted(illustrators, "Illustrator", created_book.id)
        verify_bookperson_inserted(editors, "Editor", created_book.id)
        verify_bookperson_inserted(translators, "Translator", created_book.id)
