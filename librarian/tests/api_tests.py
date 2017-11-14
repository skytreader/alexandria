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
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

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

        self.set_current_user(_creator)
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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

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

        self.set_current_user(_creator)
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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()

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

        self.set_current_user(_creator)
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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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

        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        single_author = BookRecord(
            isbn="9780062330260", title="Trigger Warning",
            genre="Short Story Collection", author=[Person(lastname="Gaiman", firstname="Neil")],
            publisher="William Morrow", publish_year=2015
        )

        single_rv = self.client.post("/api/add/books", data=single_author.request_data())

        self.assertEquals(single_rv._status_code, 200)

    def test_extra_whitespace(self):
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

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

        library = create_library(librarian.db.session, self.admin_user, roles,
          book_person_c=12, company_c=8, book_c=12, participant_c=32)

        get_books = self.client.get("/api/read/books")
        self.assertEquals(200, get_books._status_code)
        ret_data = json.loads(get_books.data)["data"]
        return_set = set()
        
        for book in ret_data:
            return_set.add(BookRecord.make_hashable(book))

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

    def test_title_edit_book(self):
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        authors = [ContributorFactory().make_plain_person() for _ in range(3)]
        book = BookRecord(isbn=fake.isbn(), title=fake.title(),
          publisher="Mumford and Sons", author=authors, publish_year=2016,
          genre="Fiction")
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        existing = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==book.isbn)
            .first()
        )
        self.assertEquals(book.title, existing.title)

        edit_data = BookRecord(isbn=book.isbn, title="This is a Ret Con",
          publisher=book.publisher, author=book.authors,
          publish_year=book.publish_year, genre=book.genre, id=book_id)
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        edited = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==book.isbn)
            .first()
        )
        self.assertEquals(edit_data.title, edited.title)

    def test_edit_book_contrib_add(self):
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        authors = [ContributorFactory().make_plain_person() for _ in range(3)]
        book = BookRecord(isbn=fake.isbn(), title=fake.title(),
          publisher="Mumford and Sons", author=authors, publish_year=2016,
          genre="Fiction")
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        additional_author = ContributorFactory().make_plain_person()
        _book_authors = copy.deepcopy(list(book.authors))
        _book_authors.append(additional_author)
        edit_data = BookRecord(isbn=book.isbn, title=book.title,
          publisher=book.publisher, author=_book_authors,
          publish_year=book.publish_year, genre=book.genre, id=book_id)
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEqual(set(_book_authors), author_persons)

    def test_edit_book_contrib_delete_deactivate(self):
        """
        Test deleting a contribution from a book where the contributor ends up
        deactivated for lack of other contributions.
        """
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        the_deleted = contributor_objs[-1]
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        self.verify_inserted(Contributor, id=the_deleted.id, active=False)

    def test_edit_book_contrib_delete_keepactive(self):
        """
        Test deleting a contribution from a book where the contributor stays
        active from other books
        """
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        # This will keep `the_deleted` alive. Get it?
        horcrux = BookRecord(
            isbn=fake.isbn(), title="Secrets of the Darkest Art",
            publisher="Scholastic", author=[the_deleted.make_plain_person()],
            publish_year=1967, genre="Black Magic"
        )
        librarian.db.session.commit()
        create_book(librarian.db.session, horcrux, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        # But the contributor remains active thanks to the horcrux!
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)

    def test_edit_book_contrib_delete_selfkeepactive(self):
        """
        Test deleting a contribution from a book where the contributor stays
        active because it is still a contributor, in another role, for the same
        book.
        """
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=2016, genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        # But the contributor remains active thanks to being the editor!
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)

    def test_edit_book_contrib_move(self):
        """
        Test that moving contributors between roles produce the desired effect.
        """
        _creator = LibrarianFactory()
        librarian.db.session.add(_creator)
        librarian.db.session.flush()
        self.set_current_user(_creator)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        the_deleted = librarian.db.session.query(Contributor).filter(Contributor.id == the_deleted.id).first()
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)
