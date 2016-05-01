# -*- coding: utf-8 -*-
from __future__ import division

from base import AppTestCase
from faker import Faker
from flask.ext.login import login_user
from librarian.models import Book, BookCompany, BookContribution, Contributor, Genre
from librarian.tests.dummies import LibraryEntry, Person
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import (
  BookFactory, BookCompanyFactory, ContributorFactory, GenreFactory, LibrarianFactory
)
from librarian.tests.utils import make_name_object, create_library

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
        self.verify_does_not_exist(Contributor, lastname="Eschenbach",
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

        single_rv = self.client.post("/api/add/books", data=single_author)

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(Contributor, lastname="Eschenbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

    def verify_bookperson_inserted(self, persons, role, bookid):
        for p in persons:
            _p = self.verify_inserted(Contributor, firstname=p["firstname"],
              lastname=p["lastname"])
            self.verify_inserted(BookContribution, person_id=_p.id,
              role_id=self.ROLE_IDS[role], book_id=bookid)

    def test_book_adder_utf8(self):
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="English 12")
        self.verify_does_not_exist(Contributor, lastname="Pérez-Reverte",
          firstname="Arturo")
        self.verify_does_not_exist(Contributor, lastname="de Onís",
          firstname="Harriet")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")

        single_author = {
            "isbn": isbn,
            "title": "The Club Dumas",
            "genre": "English 12",
            "authors": """[
                {
                    "lastname": "Pérez-Reverte",
                    "firstname": "Arturo"
                }
            ]""",
            "illustrators": "[]",
            "editors": "[]",
            "translators": """[
                {
                    "lastname": "de Onís",
                    "firstname": "Harriet"
                }
            ]""",
            "publisher": "Scholastic",
            "printer": "UP Press",
            "year": "2013"
        }

        single_rv = self.client.post("/api/add/books", data=single_author)

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="English 12")
        self.verify_inserted(Contributor, lastname="Pérez-Reverte",
          firstname="Arturo")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

    def test_book_adder_duplicate_records(self):
        _creator = LibrarianFactory()
        flask.ext.login.current_user = _creator
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(Contributor, lastname="Eschenbach",
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

        single_rv = self.client.post("/api/add/books", data=single_author)

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(Contributor, lastname="Eschenbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

        duplicate = self.client.post("/api/add/books", data=single_author)

        self.assertEquals(duplicate._status_code, 409)
        

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

        req_val = self.client.post("/api/add/books", data=req_data)
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
                bp = Contributor(firstname=p["firstname"],
                  lastname=p["lastname"], creator_id=self.admin_user.id)
                librarian.db.session.add(bp)

            librarian.db.session.flush()
        
        def verify_bookperson(p):
            self.verify_inserted(Contributor, firstname=p["firstname"],
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

        req_val = self.client.post("/api/add/books", data=req_data)
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

        single_rv = self.client.post("/api/add/books", data=single_author)

        self.assertEquals(single_rv._status_code, 200)

    def test_multiple_same_names(self):
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
                },
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

        single_rv = self.client.post("/api/add/books", data=single_author)
        self.assertEquals(200, single_rv.status_code)
        
        gaimen = (librarian.db.session.query(Contributor)
          .filter(Contributor.firstname == 'Neil')
          .filter(Contributor.lastname == 'Gaiman').all())

        self.assertEquals(1, len(gaimen))

    def test_servertime(self):
        servertime = self.client.get("/api/util/servertime")
        self.assertEquals(servertime._status_code, 200)
        data = json.loads(servertime.data)
        self.assertTrue(dateutil.parser.parse(data["now"]))

    def test_list_genres(self):
        empty_genres = self.client.get("/api/read/genres")
        data = json.loads(empty_genres.data)
        self.assertEqual(set(), set(data["data"]))

        genres = [GenreFactory() for _ in range(8)]

        for g in genres:
            librarian.db.session.add(g)

        librarian.db.session.flush()
        expected_genre_set = set([g.name for g in genres])

        list_genres = self.client.get("/api/read/genres")
        data = json.loads(list_genres.data)
        genre_set = set(data["data"])

        self.assertEqual(expected_genre_set, genre_set)

    def test_list_companies(self):
        empty_companies = self.client.get("/api/read/companies")
        data = json.loads(empty_companies.data)
        self.assertEqual(set(), set(data["data"]))

        companies = [BookCompanyFactory() for _ in range(8)]

        for c in companies:
            librarian.db.session.add(c)

        librarian.db.session.flush()
        expected_company_set = set([c.name for c in companies])

        list_companies = self.client.get("/api/read/companies")
        data = json.loads(list_companies.data)
        company_set = set(data["data"])

        self.assertEqual(expected_company_set, company_set)

    def test_list_persons(self):
        empty = json.loads(self.client.get("/api/read/persons").data)
        self.assertEqual(len(empty["data"]), 0)

        persons = [ContributorFactory() for _ in range(8)]

        for p in persons:
            librarian.db.session.add(p)

        librarian.db.session.flush()
        expected_person_set = set([Person(p.lastname, p.firstname) for p in persons])

        list_persons = self.client.get("/api/read/persons")
        data = json.loads(list_persons.data)
        person_set = set([Person(p["lastname"], p["firstname"]) for p in data["data"]])

        self.assertEqual(expected_person_set, person_set)

    def test_get_books(self):
        library = create_library(librarian.db.session, self.admin_user,
          self.ROLE_IDS, book_person_c=12, company_c=8, book_c=12, participant_c=32)
        get_books = self.client.get("/api/read/books")
        self.assertEquals(200, get_books._status_code)
        ret_data = json.loads(get_books.data)["data"]
        return_set = set()
        
        for book in ret_data:
            return_set.add(LibraryEntry(**book))

        self.assertEquals(set(library), return_set)

    def test_stats(self):
        person_count = 44
        company_count = 9
        book_count = 28
        participant_count = 33
        library = create_library(librarian.db.session, self.admin_user,
          self.ROLE_IDS, book_person_c=person_count, company_c=company_count,
          book_c=book_count, participant_c=participant_count)

        get_stats = self.client.get("/api/util/stats")
        stats = json.loads(get_stats.data)
        
        self.assertEquals(200, get_stats._status_code)
        
        participants_per_book = participant_count / book_count
        self.assertEquals(participants_per_book, stats.get("participants_per_book"))
