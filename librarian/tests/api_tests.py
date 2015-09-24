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
                    "lastname": "Eschenbach",
                    "firstname": "Andreas"
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

    def make_name_object(self):
        name = fake.name().split()
        is_roman_num = PROLLY_ROMAN_NUM.match(name[-1])
        last_name = " ".join(name[-1:]) if is_roman_num else name[-1]
        first_name = name[0]

        return {"firstname": first_name, "lastname": last_name}

    def verify_bookperson_inserted(self, persons, role, bookid):
        for p in persons:
            _p = self.verify_inserted(BookPerson, firstname=p["firstname"],
              lastname=p["lastname"])
            self.verify_inserted(BookParticipant, person_id=_p.id,
              role_id=self.ROLE_IDS[role], book_id=bookid)

    def test_multiple_book_people(self):
        """
        Test adding multiple people for the fields where person names are
        expected. We can assume that records are "fresh".
        """
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()
        title = fake.title()

        authors = [self.make_name_object() for _ in range(4)]
        illustrators = [self.make_name_object() for _ in range(4)]
        editors = [self.make_name_object() for _ in range(4)]
        translators = [self.make_name_object() for _ in range(4)]

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
        
        self.verify_bookperson_inserted(authors, "Author", created_book.id)
        self.verify_bookperson_inserted(illustrators, "Illustrator", created_book.id)
        self.verify_bookperson_inserted(editors, "Editor", created_book.id)
        self.verify_bookperson_inserted(translators, "Translator", created_book.id)

    def test_repeat_people(self):
        """
        Test that API call should still succeed even if the people have been
        added before.
        """

        def insert_bookpersons(persons):
            for p in persons:
                bp = BookPerson(firstname=p["firstname"],
                  lastname=p["lastname"], creator=self.admin_user.id)
                librarian.db.session.add(bp)

            librarian.db.session.flush()
        
        def verify_bookperson(p):
            self.verify_inserted(BookPerson, firstname=p["firstname"],
              lastname=p["lastname"])

        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()
        title = fake.title()

        authors = [self.make_name_object() for _ in range(4)]
        insert_bookpersons(authors)
        map(verify_bookperson, authors)
      
        illustrators = [self.make_name_object() for _ in range(4)]
        insert_bookpersons(illustrators)
        map(verify_bookperson, illustrators)
        
        editors = [self.make_name_object() for _ in range(4)]
        insert_bookpersons(editors)
        map(verify_bookperson, editors)
        
        translators = [self.make_name_object() for _ in range(4)]
        insert_bookpersons(translators)
        map(verify_bookperson, translators)

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

    def test_no_printer(self):
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        single_author = {
            "isbn": "9780062330260",
            "title": "Trigger Warning",
            "genre": "Short Story Collection",
            "authors": """[
                {
                    "lastname": "Gaiman",
                    "firstname": "Neil"
                }
            ]""",
            "illustrators": "[]",
            "editors": "[]",
            "translators": "[]",
            "publisher": "Wiliam Morrow",
            "printer": "",
            "year": "2015"
        }

        single_rv = self.client.post("/api/book_adder", data=single_author)

        self.assertEquals(single_rv._status_code, 200)
