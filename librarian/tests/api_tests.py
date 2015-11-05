from base import AppTestCase
from faker import Faker
from flask.ext.login import login_user
from librarian.models import Book, BookCompany, BookParticipant, BookPerson, Genre
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import (
  BookCompanyFactory, BookPersonFactory, GenreFactory, LibrarianFactory
)
from librarian.tests.utils import make_name_object

import dateutil.parser
import factory
import flask.ext.login
import json
import librarian
import random
import re
import string
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

        authors = [make_name_object() for _ in range(4)]
        insert_bookpersons(authors)
        map(verify_bookperson, authors)
      
        illustrators = [make_name_object() for _ in range(4)]
        insert_bookpersons(illustrators)
        map(verify_bookperson, illustrators)
        
        editors = [make_name_object() for _ in range(4)]
        insert_bookpersons(editors)
        map(verify_bookperson, editors)
        
        translators = [make_name_object() for _ in range(4)]
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

    def test_servertime(self):
        servertime = self.client.get("/api/util/servertime")
        self.assertEquals(servertime._status_code, 200)
        data = json.loads(servertime.data)
        self.assertTrue(dateutil.parser.parse(data["now"]))

    def test_list_genres(self):
        genres = [GenreFactory() for _ in range(8)]

        for g in genres:
            librarian.db.session.add(g)

        librarian.db.session.flush()
        expected_genre_set = set([g.name for g in genres])

        list_genres = self.client.get("/api/list/genres")
        data = json.loads(list_genres.data)
        genre_set = set(data["data"])

        self.assertEqual(expected_genre_set, genre_set)

    def test_list_companies(self):
        companies = [BookCompanyFactory() for _ in range(8)]

        for c in companies:
            librarian.db.session.add(c)

        librarian.db.session.flush()
        expected_company_set = set([c.name for c in companies])

        list_companies = self.client.get("/api/list/companies")
        data = json.loads(list_companies.data)
        company_set = set(data["data"])

        self.assertEqual(expected_company_set, company_set)

    def test_list_persons(self):
        class Person:
            def __init__(self, lastname, firstname):
                self.lastname = lastname
                self.firstname = firstname

            def __eq__(self, p):
                return p.lastname == self.lastname and p.firstname == self.firstname

            def __hash__(self):
                return hash((self.lastname, self.firstname))
            
            def __str__(self):
                return self.lastname + ", " + self.firstname

        empty = json.loads(self.client.get("/api/list/persons").data)
        self.assertEqual(len(empty["data"]), 0)

        persons = [BookPersonFactory() for _ in range(8)]

        for p in persons:
            librarian.db.session.add(p)

        librarian.db.session.flush()
        expected_person_set = set([Person(p.lastname, p.firstname) for p in persons])

        list_persons = self.client.get("/api/list/persons")
        data = json.loads(list_persons.data)
        person_set = set([Person(p["lastname"], p["firstname"]) for p in data["data"]])

        self.assertEqual(expected_person_set, person_set)

    def test_get_books(self):
        book_persons = [BookPersonFactory() for _ in range(8)]

        for bp in book_persons:
            librarian.db.session.add(bp)

        books = [BookFactory() for _ in range(12)]

        for b in books:
            librarian.db.session.add(b)

        library = {}
        # Randomly assign persons to books as roles
        roles = self.ROLE_IDS.keys()

        for _ in range(32):
            rand_book = random.choice(books)
            rand_person = random.choice(book_persons)
            rand_role = random.choice(roles)

            if library.get(rand_book.isbn):
                if library[rand_book.isbn].get(rand_role):
                    pass
                else:
                    library[rand_book.isbn][rand_role] = {"lastname": rand_person. lastname,
                      "firstname": rand_person.firstname}

                    bp = BookParticipant(book_id=rand_book.id,
                      person_id=rand_person.id, role_id=self.ROLE_IDS[rand_role])
                    librarian.db.session.add(bp)
            else:
                library[rand_book.isbn]["title"] = rand_book.title
                library[rand_book.isbn][rand_role] = {"lastname": rand_person.lastname,
                  "firstname": rand_person.firstname}
                bp = BookParticipant(book_id=rand_book.id,
                  person_id=rand_person.id, role_id=self.ROLE_IDS[rand_role])

        librarian.db.session.flush()

        get_books = self.client.get("/api/get/books")
        self.assertEquals(library, get_books)
