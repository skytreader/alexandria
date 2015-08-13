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
        the_carpet_makers = librarian.db.session.query(Book).filter(Book.isbn == isbn).all()
        self.assertEquals([], the_carpet_makers)
        io9_genre = librarian.db.session.query(Genre).filter(Genre.name=="io9").all()
        self.assertEquals([], io9_genre)
        aeschenbach = (librarian.db.session.query(BookPerson)
          .filter(BookPerson.lastname=="Eschenbach")
          .filter(BookPerson.firstname=="Andreas").all())
        self.assertEquals([], aeschenbach)
        scholastic = (librarian.db.session.query(BookCompany)
          .filter(BookCompany.name=="Scholastic").all())
        self.assertEquals([], scholastic)
        up_press = (librarian.db.session.query(BookCompany)
          .filter(BookCompany.name=="UP Press").all())
        self.assertEquals([], up_press)

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

        the_carpet_makers = librarian.db.session.query(Book).filter(Book.isbn == isbn).all()
        self.assertEquals(1, len(the_carpet_makers))
        io9_genre = librarian.db.session.query(Genre).filter(Genre.name=="io9").all()
        self.assertEquals(1, len(io9_genre))
        aeschenbach = (librarian.db.session.query(BookPerson)
          .filter(BookPerson.lastname=="Eschenbach")
          .filter(BookPerson.firstname=="Andreas").all())
        self.assertEquals(1, len(aeschenbach))
        scholastic = (librarian.db.session.query(BookCompany)
          .filter(BookCompany.name=="Scholastic").all())
        self.assertEquals(1, len(scholastic))
        up_press = (librarian.db.session.query(BookCompany)
          .filter(BookCompany.name=="UP Press").all())
        self.assertEquals(1, len(up_press))

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

        for auth in authors:
            auth = (librarian.db.session.query(BookPerson)
              .filter(BookPerson.firstname==auth["first_name"])
              .filter(BookPerson.lastname==auth["last_name"]).all())
            
            self.assertEqual(1, len(auth))
            
            participant = (librarian.db.session.query(BookParticipant)
              .filter(BookParticipant.person_id==auth[0].id)
              .filter(BookParticipant.role_id==self.ROLE_IDS["Author"])
              .filter(BookParticipant.book_id==created_book.id).all())

            self.assertEqual(1, len(participant))
