# -*- coding: utf-8 -*-
from __future__ import division

from base import AppTestCase
from faker import Faker
from flask_login import login_user
from librarian.models import Book, BookCompany, BookContribution, Contributor, Genre, Role
from librarian.utils import BookRecord, Person
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import (
  BookCompanyFactory, ContributorFactory, GenreFactory, LibrarianFactory
)
from librarian.tests.utils import (
    make_person_object, create_library, create_book
)

import copy
import dateutil.parser
import factory
import flask_login
import json
import librarian
import librarian.api as api
import math
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
        self.make_current_user()
        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")
        author = [Person(lastname="Eschbach", firstname="Andreas")]

        single_author = BookRecord(
            isbn=isbn, title="The Carpet Makers", genre="io9", author=author,
            publisher="Scholastic", printer="UP Press", publish_year=2013
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

    def test_book_adder_blank_person(self):
        self.make_current_user()
        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")
        author = [Person(lastname="", firstname="")]

        single_author = BookRecord(
            isbn=isbn, title="The Carpet Makers", genre="io9", author=author,
            publisher="Scholastic", printer="UP Press", publish_year=2013
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 400)

        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")

    def test_book_adder_reactivation(self):
        self.set_current_user(self.admin_user)
        inactive_contributor = ContributorFactory(
            lastname="Duffer", firstname="Matt", active=False
        )
        librarian.db.session.add(inactive_contributor)
        librarian.db.session.flush()

        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="Horror")
        self.verify_does_not_exist(BookCompany, name="Netflix")
        self.verify_does_not_exist(BookCompany, name="WWW")
        author = [Person(lastname="Duffer", firstname="Matt")]

        single_author = BookRecord(
            isbn=isbn, title="Stranger Things", genre="Horror", author=author,
            publisher="Netflix", printer="WWW", publish_year=2016
        )

        reactivate = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(reactivate._status_code, 200)
        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="Horror")
        self.verify_inserted(BookCompany, name="Netflix")
        self.verify_inserted(BookCompany, name="WWW")
        self.verify_inserted(
            Contributor, lastname="Duffer", firstname="Matt", active=True
        )

    def test_book_adder_no_printer(self):
        self.make_current_user()
        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")
        author = [Person(lastname="Eschbach", firstname="Andreas")]

        single_author = BookRecord(
            isbn=isbn, title="The Carpet Makers", genre="io9", author=author,
            publisher="Scholastic", publish_year=2013
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="")

    def verify_persons_inserted(self, persons, role, bookid):
        for p in persons:
            _p = self.verify_inserted(Contributor, firstname=p.firstname,
              lastname=p.lastname)
            self.verify_inserted(BookContribution, contributor_id=_p.id,
              role_id=self.ROLE_IDS[role], book_id=bookid)

    def test_book_adder_utf8(self):
        self.make_current_user()
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
        author = [Person(lastname="Pérez-Reverte", firstname="Arturo")]
        translator = [Person(lastname="de Onís", firstname="Harriet")]
        single_author = BookRecord(
            isbn=isbn, title="The Club Dumas", genre="English 12", author=author,
            translator=translator, publisher="Scholastic", printer="UP Press",
            publish_year=2013
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="English 12")
        self.verify_inserted(Contributor, lastname="Pérez-Reverte",
          firstname="Arturo")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

    def test_book_adder_duplicate_records(self):
        self.make_current_user()
        isbn = fake.isbn()

        # Check that the relevant records do not exist yet
        self.verify_does_not_exist(Book, isbn=isbn)
        self.verify_does_not_exist(Genre, name="io9")
        self.verify_does_not_exist(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_does_not_exist(BookCompany, name="Scholastic")
        self.verify_does_not_exist(BookCompany, name="UP Press")

        author = [Person(lastname="Eschbach", firstname="Andreas")]
        single_author = BookRecord(
            isbn=isbn, title="The Carpet Makers", genre="io9", author=author,
            publisher="Scholastic", printer="UP Press", publish_year=2013
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

        self.verify_inserted(Book, isbn=isbn)
        self.verify_inserted(Genre, name="io9")
        self.verify_inserted(Contributor, lastname="Eschbach",
          firstname="Andreas")
        self.verify_inserted(BookCompany, name="Scholastic")
        self.verify_inserted(BookCompany, name="UP Press")

        duplicate = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(duplicate._status_code, 409)
        
    def test_book_adder_duplicate_isbn13(self):
        self.make_current_user()
        isbn13 = "9781596914698"

        self.verify_does_not_exist(Book, isbn=isbn13)
        self.verify_does_not_exist(Genre, name="Academic Nonfiction")
        self.verify_does_not_exist(Contributor, lastname="Bayard", firstname="Pierre")
        self.verify_does_not_exist(Contributor, lastname="Mehlman", firstname="Jeffrey")
        self.verify_does_not_exist(BookCompany, name="Bloomsbury")
        self.verify_does_not_exist(BookCompany, name="Quebecor World Fairfield")

        author = [Person(lastname="Bayard", firstname="Pierre")]
        translator = [Person(lastname="Mehlman", firstname="Jeffrey")]
        books_you_havent_read = BookRecord(
            isbn=isbn13, title="How to Talk About Books You Haven't Read",
            author=author, translator=translator, genre="Academic Nonfiction",
            publisher="Bloomsbury", printer="Quebecor World Fairfield", 
            publish_year=2007
        )

        havent_read_rv = self.client.post("/api/add/books", data=books_you_havent_read.request_data())

        self.verify_inserted(Book, isbn=isbn13)
        self.verify_inserted(Genre, name="Academic Nonfiction")
        self.verify_inserted(Contributor, lastname="Bayard", firstname="Pierre")
        self.verify_inserted(Contributor, lastname="Mehlman", firstname="Jeffrey")
        self.verify_inserted(BookCompany, name="Bloomsbury")
        self.verify_inserted(BookCompany, name="Quebecor World Fairfield")

        books_you_havent_read.isbn = "1596914696"

        duplicate = self.client.post("/api/add/books", data=books_you_havent_read.request_data())

        self.assertEquals(duplicate._status_code, 409)

    def test_book_adder_duplicate_isbn10(self):
        """
        Switch ISBNs of test_book_adder_duplicate_isbn13.
        """
        self.make_current_user()
        isbn13 = "1596914696"

        self.verify_does_not_exist(Book, isbn=isbn13)
        self.verify_does_not_exist(Genre, name="Academic Nonfiction")
        self.verify_does_not_exist(Contributor, lastname="Bayard", firstname="Pierre")
        self.verify_does_not_exist(Contributor, lastname="Mehlman", firstname="Jeffrey")
        self.verify_does_not_exist(BookCompany, name="Bloomsbury")
        self.verify_does_not_exist(BookCompany, name="Quebecor World Fairfield")

        author = [Person(lastname="Bayard", firstname="Pierre")]
        translator = [Person(lastname="Mehlman", firstname="Jeffrey")]
        books_you_havent_read = BookRecord(
            isbn=isbn13, title="How to Talk About Books You Haven't Read",
            author=author, translator=translator, genre="Academic Nonfiction",
            publisher="Bloomsbury", printer="Quebecor World Fairfield", 
            publish_year=2007
        )

        havent_read_rv = self.client.post("/api/add/books", data=books_you_havent_read.request_data())

        self.verify_inserted(Book, isbn=isbn13)
        self.verify_inserted(Genre, name="Academic Nonfiction")
        self.verify_inserted(Contributor, lastname="Bayard", firstname="Pierre")
        self.verify_inserted(Contributor, lastname="Mehlman", firstname="Jeffrey")
        self.verify_inserted(BookCompany, name="Bloomsbury")
        self.verify_inserted(BookCompany, name="Quebecor World Fairfield")

        books_you_havent_read.isbn = "9781596914698"

        duplicate = self.client.post("/api/add/books", data=books_you_havent_read.request_data())

        self.assertEquals(duplicate._status_code, 409)

    def test_multiple_book_people(self):
        """
        Test adding multiple people for the fields where person names are
        expected. We can assume that records are "fresh".
        """
        self.make_current_user()
        isbn = fake.isbn()
        title = fake.title()

        authors = [make_person_object() for _ in range(4)]
        illustrators = [make_person_object() for _ in range(4)]
        editors = [make_person_object() for _ in range(4)]
        translators = [make_person_object() for _ in range(4)]

        req_data = BookRecord(
            isbn=isbn, title=title, genre="Multinational", author=authors,
            illustrator=illustrators, editor=editors, translator=translators,
            publisher="Scholastic", printer="UP Press", publish_year=2013
        )

        req_val = self.client.post("/api/add/books", data=req_data.request_data())
        self.assertEqual(200, req_val.status_code)
        created_book = (librarian.db.session.query(Book)
          .filter(Book.isbn==isbn).first())
        
        self.verify_persons_inserted(authors, "Author", created_book.id)
        self.verify_persons_inserted(illustrators, "Illustrator", created_book.id)
        self.verify_persons_inserted(editors, "Editor", created_book.id)
        self.verify_persons_inserted(translators, "Translator", created_book.id)

    def test_repeat_people(self):
        """
        Test that API call should still succeed even if the people have been
        added before.
        """

        def insert_bookpersons(persons):
            for p in persons:
                bp = Contributor(firstname=p.firstname,
                  lastname=p.lastname, creator=self.admin_user)
                librarian.db.session.add(bp)

            librarian.db.session.flush()
        
        def verify_bookperson(p):
            self.verify_inserted(Contributor, firstname=p.firstname,
              lastname=p.lastname)

        self.make_current_user()
        isbn = fake.isbn()
        title = fake.title()

        authors = [make_person_object() for _ in range(4)]
        insert_bookpersons(authors)
        map(verify_bookperson, authors)
      
        illustrators = [make_person_object() for _ in range(4)]
        insert_bookpersons(illustrators)
        map(verify_bookperson, illustrators)
        
        editors = [make_person_object() for _ in range(4)]
        insert_bookpersons(editors)
        map(verify_bookperson, editors)
        
        translators = [make_person_object() for _ in range(4)]
        insert_bookpersons(translators)
        map(verify_bookperson, translators)

        req_data = BookRecord(
            isbn=isbn, title=title, genre="Multinational", author=authors,
            illustrator=illustrators, editor=editors, translator=translators,
            publisher="Scholastic", printer="UP Press", publish_year=2013
        )

        req_val = self.client.post("/api/add/books", data=req_data.request_data())
        self.assertEqual(200, req_val.status_code)

    def test_no_printer(self):
        self.make_current_user()
        single_author = BookRecord(
            isbn="9780062330260", title="Trigger Warning",
            genre="Short Story Collection", author=[Person(lastname="Gaiman", firstname="Neil")],
            publisher="William Morrow", publish_year=2015
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

    def test_extra_whitespace(self):
        self.make_current_user()
        self.verify_does_not_exist(
            Contributor, lastname="de Cervantes", firstname="Miguel"
        )

        spaced = BookRecord(
            isbn="0812972104", title="Don Quixote", genre="Fiction",
            author=[Person(lastname="  de Cervantes  ", firstname="Miguel")],
            publisher="Modern Library", publish_year=2006
        )

        spaced_rv = self.client.post("/api/add/books", data=spaced.request_data())
        self.assertEquals(200, spaced_rv.status_code)

        self.verify_inserted(
            Contributor, lastname="de Cervantes", firstname="Miguel"
        )

    def test_multiple_same_names(self):
        self.make_current_user()
        Neil_Gaiman = Person(lastname="Gaiman", firstname="Neil")
        single_author = BookRecord(
            isbn="9780062330260", title="Trigger Warning",
            genre="Short Story Collection", author=[Neil_Gaiman, Neil_Gaiman],
            publisher="William Morrow", publish_year=2015
        )
        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(200, single_rv.status_code)
        
        gaimen = (librarian.db.session.query(Contributor)
          .filter(Contributor.firstname == 'Neil')
          .filter(Contributor.lastname == 'Gaiman').all())

        self.assertEquals(1, len(gaimen))

    def test_genre_adding(self):
        g1 = GenreFactory(name="B Genre")
        g2 = GenreFactory(name="A Genre")
        librarian.db.session.add(g1)
        librarian.db.session.add(g2)
        librarian.db.session.flush()
        self.set_current_user(self.admin_user)

        bgenre_book = BookRecord(
            isbn=fake.isbn(), title=fake.title(), genre=g1.name,
            author=[make_person_object()], publisher="random",
            publish_year=2017
        )
        bgenre_rv = self.client.post("/api/add/books", data=bgenre_book.request_data())
        self.assertEquals(200, bgenre_rv.status_code)

        agenre_book = BookRecord(
            isbn=fake.isbn(), title=fake.title(), genre=g2.name,
            author=[make_person_object()], publisher="random",
            publish_year=2017
        )
        agenre_rv = self.client.post("/api/add/books", data=agenre_book.request_data())
        self.assertEquals(200, agenre_rv.status_code)

        bgenre_orm = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==bgenre_book.isbn)
            .first()
        )

        agenre_orm = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==agenre_book.isbn)
            .first()
        )

        self.assertNotEquals(bgenre_orm.genre, agenre_orm.genre)
        self.assertEquals(bgenre_orm.genre.name, g1.name)
        self.assertEquals(agenre_orm.genre.name, g2.name)

    def test_same_person_diff_roles(self):
        self.make_current_user()
        jtamaki_exists = (
            librarian.db.session.query(Contributor)
            .filter(Contributor.firstname == "Jillian")
            .filter(Contributor.lastname == "Tamaki")
            .first()
        )
        self.assertFalse(jtamaki_exists)
        
        jtamaki = Person(lastname="Tamaki", firstname="Jillian")
        author_illus = BookRecord(
            isbn="9781596437746", title="This One Summer", genre="Graphic Novel",
            author=[jtamaki], illustrator=[jtamaki], publisher="First Second",
            publish_year=2016
        )
        rv = self.client.post("/api/add/books", data=author_illus.request_data())

        self.assertEquals(200, rv.status_code)

        jtamakis = (
            librarian.db.session.query(Contributor)
            .filter(Contributor.firstname == "Jillian")
            .filter(Contributor.lastname == "Tamaki")
            .all()
        )
        self.assertEqual(1, len(jtamakis))

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

        inactive = ContributorFactory(lastname="GLadwell", firstname="MAlcolm III", active=False)
        librarian.db.session.add(inactive)

        librarian.db.session.flush()
        expected_person_set = set([Person(p.lastname, p.firstname) for p in persons])

        list_persons = self.client.get("/api/read/persons")
        data = json.loads(list_persons.data)
        person_set = set([Person(p["lastname"], p["firstname"]) for p in data["data"]])

        self.assertEqual(expected_person_set, person_set)

        inactive.active = True
        librarian.db.session.flush()
        expected_person_set.add(Person(inactive.lastname, inactive.firstname))
        list_persons = self.client.get("/api/read/persons")
        data = json.loads(list_persons.data)
        person_set = set([Person(p["lastname"], p["firstname"]) for p in data["data"]])

        self.assertEqual(expected_person_set, person_set)

    def test_get_books(self):
        roles = librarian.db.session.query(Role).all()
        book_count = 12

        library = create_library(librarian.db.session, self.admin_user, roles,
          book_person_c=12, company_c=8, book_c=book_count, participant_c=32)

        get_books = self.client.get("/api/read/books?limit=%s" % book_count)
        self.assertEquals(200, get_books._status_code)
        ret_data = json.loads(get_books.data)["data"]
        return_set = set()
        
        for book in ret_data:
            return_set.add(BookRecord.make_hashable(book))

        self.assertEquals(set(library), return_set)

    def test_get_books_offset(self):
        roles = librarian.db.session.query(Role).all()
        book_count = 12
        limit = 8

        library = create_library(librarian.db.session, self.admin_user, roles,
          book_person_c=12, company_c=8, book_c=book_count, participant_c=32)

        returned_books = 0
        offset = 0
        return_set = set()
        max_iters = int(math.ceil(book_count / limit))

        # There is a flaky issue with this test that sometimes, the first get
        # books returns one less record than is supposedly available. I have no
        # idea why it happens so I added the max_iters limiter so that this loop
        # has an explicit bound. Oddly, that seems to have solved the problem.
        while returned_books < book_count and offset < max_iters:
            get_books = self.client.get("/api/read/books?offset=%s&limit=%s" % (offset, 8))
            self.assertEquals(200, get_books._status_code)
            ret_data = json.loads(get_books.data)["data"]
            returned_books += len(ret_data)
            
            for book in ret_data:
                return_set.add(BookRecord.make_hashable(book))

            offset += 1

        self.assertEquals(returned_books, book_count)
        self.assertEquals(set(library), return_set)

    def test_stats(self):
        person_count = 44
        company_count = 9
        book_count = 28
        participant_count = 33
        roles = librarian.db.session.query(Role).all()
        library = create_library(librarian.db.session, self.admin_user, roles,
          book_person_c=person_count, company_c=company_count, book_c=book_count,
          participant_c=participant_count)

        get_stats = self.client.get("/api/util/stats")
        stats = json.loads(get_stats.data)
        
        self.assertEquals(200, get_stats._status_code)
        
        participants_per_book = participant_count / book_count
        self.assertEquals(participants_per_book, stats.get("participants_per_book"))

    def test_search_title(self):
        search_book = BookRecord(
            isbn=fake.isbn(), title="Find XYZ Inside", publisher="Creative Awesome",
            publish_year=2017, author=[Person("Munroe", "Randall")], genre="Test"
        )
        create_book(librarian.db.session, search_book, self.admin_user)
        librarian.db.session.flush()
        results = api.search("XYZ")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

        results = api.search("xyz")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

    def test_search_isbn(self):
        search_book = BookRecord(
            isbn=fake.isbn(), title="Find XYZ Inside", publisher="Creative Awesome",
            publish_year=2017, author=[Person("Munroe", "Randall")], genre="Test"
        )
        create_book(librarian.db.session, search_book, self.admin_user)
        librarian.db.session.flush()
        results = api.search(search_book.isbn)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

    def test_search_publisher(self):
        search_book = BookRecord(
            isbn=fake.isbn(), title="Totally Unrelated to Search Query",
            publisher="Walnut Publishing", publish_year=2017,
            author=[Person("Hawking", "Stevie")], genre="Test"
        )
        create_book(librarian.db.session, search_book, self.admin_user)
        librarian.db.session.flush()
        results = api.search("walnut")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

    def test_search_contributor(self):
        search_book = BookRecord(
            isbn=fake.isbn(), title="Don Quixote", publisher="Instituto Cervantes",
            publish_year=1957, author=[Person("de Cervantes Saavedra", "Miguel")],
            genre="Sci-Fi"
        )
        create_book(librarian.db.session, search_book, self.admin_user)
        librarian.db.session.flush()
        results = api.search("Cervantes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

        results = api.search("cervantes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)

        results = api.search("miguel de cervantes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["isbn"], search_book.isbn)
