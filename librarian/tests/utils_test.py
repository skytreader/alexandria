# -*- coding: utf-8 -*-
from base import AppTestCase
from faker import Faker
from librarian.models import Book, BookCompany, BookContribution, Contributor, Role
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookContributionFactory, BookFactory, ContributorFactory
from librarian.tests import utils
from librarian.utils import BookRecord, isbn_check, Person

import copy
import unittest
import librarian

class IsbnTests(unittest.TestCase):
    
    def test_specified(self):
        isbn10_correct = "0306406152"
        isbn13_correct = "9780306406157"

        isbn10_incorrect = "0306406155"
        isbn13_incorrect = "9780306406155"

        self.assertTrue(isbn_check(isbn10_correct))
        self.assertTrue(isbn_check(isbn13_correct))
        self.assertFalse(isbn_check(isbn10_incorrect))
        self.assertFalse(isbn_check(isbn13_incorrect))
        
        self.assertFalse(isbn_check("lettersabc"))
        self.assertFalse(isbn_check("123456789"))

    def test_faker(self):
        fake = Faker()
        fake.add_provider(BookFieldsProvider)
        # dual-validation
        for i in range(100):
            self.assertTrue(isbn_check(fake.isbn()))

        for i in range(100):
            self.assertTrue(isbn_check(fake.isbn(False)))

class BookRecordTests(AppTestCase):
    
    def test_assembler(self):
        # Create the DB records
        booka = BookFactory()

        booka_author = BookContributionFactory(role=Role.get_preset_role("Author"),
          book=booka)
        librarian.db.session.add(booka_author)
        booka_translator = BookContributionFactory(role=Role.get_preset_role("Translator"),
          book=booka)
        librarian.db.session.add(booka_translator)
        booka_illus1 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=booka)
        librarian.db.session.add(booka_illus1)
        librarian.db.session.commit()
        booka_illus2 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=booka)
        librarian.db.session.add(booka_illus2)
        librarian.db.session.commit()

        bookb = BookFactory()
        bookb_author = BookContributionFactory(role=Role.get_preset_role("Author"),
          book=bookb)
        bookb_translator = BookContributionFactory(role=Role.get_preset_role("Translator"),
          book=bookb)
        bookb_illus = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=bookb)
        self.session_add_all((bookb_author, bookb_translator, bookb_illus))
        librarian.db.session.flush()

        # Create the BookRecord objects
        booka_authors = [booka_author.contributor.make_plain_person()]
        booka_translators = [booka_translator.contributor.make_plain_person()]
        booka_illustrators = [booka_illus1.contributor.make_plain_person(),
          booka_illus2.contributor.make_plain_person()]
        booka_record = BookRecord(isbn=booka.isbn, title=booka.title,
          publisher=booka.publisher.name, author=booka_authors,
          translator=booka_translators, illustrator=booka_illustrators,
          id=booka.id)

        bookb_authors = [bookb_author.contributor.make_plain_person()]
        bookb_translators = [bookb_translator.contributor.make_plain_person()]
        bookb_illustrators = [bookb_illus.contributor.make_plain_person()]
        bookb_record = BookRecord(isbn=bookb.isbn, title=bookb.title,
          publisher=bookb.publisher.name, author=bookb_authors,
          translator=bookb_translators, illustrator=bookb_illustrators,
          id=bookb.id)

        expected_records = [booka_record, bookb_record]

        bookq = (librarian.db.session.query(Book.id, Book.isbn, Book.title,
          Contributor.lastname, Contributor.firstname, Role.name,
          BookCompany.name)
          .filter(Book.id == BookContribution.book_id)
          .filter(BookContribution.contributor_id == Contributor.id)
          .filter(BookContribution.role_id == Role.id)
          .filter(Book.publisher_id == BookCompany.id))

        books = bookq.all()
        
        set(expected_records)
        self.assertEqual(set(expected_records), set(BookRecord.assembler(books)))

    def test_deepcopy(self):
        fake = Faker()
        fake.add_provider(BookFieldsProvider)
        authors = [ContributorFactory().make_plain_person() for _ in range(3)]
        book = BookRecord(isbn=fake.isbn(), title=fake.title(),
          publisher="Firaxis", author=authors, publish_year=2016,
          genre="Fiction")

        _book = copy.deepcopy(book)
        self.assertTrue(book is not _book)
        original_attrs = book.__dict__
        deepcopy_attrs = _book.__dict__
        attrs = original_attrs.keys()
        self.assertEquals(attrs, deepcopy_attrs.keys())

        for a in attrs:
            orig_type = type(original_attrs[a])
            copy_type = type(deepcopy_attrs[a])
            self.assertTrue(orig_type is copy_type)

            if a in BookRecord.LIST_TYPES:
                original_persons = [Person(**pdict) for pdict in original_attrs[a]]
                deepcopy_persons = [Person(**pdict) for pdict in deepcopy_attrs[a]]
                self.assertEquals(set(original_persons), set(deepcopy_persons))
            else:
                self.assertEquals(original_attrs[a], deepcopy_attrs[a])

        authors.append(Person(firstname="Sid", lastname="Meier"))
        _book.authors = frozenset(authors)
        self.assertNotEquals(book.authors, _book.authors)

class PersonTests(AppTestCase):
    
    def test_deepcopy(self):
        ronaldo = Person(firstname="Ronaldo", lastname="Nazario")
        cr7 = copy.deepcopy(ronaldo)
        self.assertFalse(cr7 is ronaldo)

class FunctionsTests(AppTestCase):
    
    def test_create_library(self):
        contribs = librarian.db.session.query(Contributor).all()
        self.assertEquals(0, len(contribs))
        companies = librarian.db.session.query(BookCompany).all()
        self.assertEquals(0, len(companies))
        books = librarian.db.session.query(Book).all()
        self.assertEquals(0, len(books))
        a_contribs = librarian.db.session.query(BookContribution).all()
        self.assertEquals(0, len(a_contribs))

        roles = librarian.db.session.query(Role).all()

        library = utils.create_library(librarian.db.session, self.admin_user,
          roles, book_person_c=12, company_c=8, book_c=12, participant_c=32)

        contribs = librarian.db.session.query(Contributor).all()
        self.assertEquals(12, len(contribs))
        companies = librarian.db.session.query(BookCompany).all()
        self.assertEquals(8, len(companies))
        books = librarian.db.session.query(Book).all()
        self.assertEquals(12, len(books))
        a_contribs = librarian.db.session.query(BookContribution).all()
        self.assertEquals(32, len(a_contribs))

    def test_create_book(self):
        sample_isbn = "9780306406157"
        # ensure it does not exist
        bookq = librarian.db.session.query(Book).filter(Book.isbn==sample_isbn)
        book = bookq.first()

        self.assertTrue(book is None)
        br = BookRecord(isbn=sample_isbn, title="Another Chance for Poland",
          publisher="Eurosport", author=(Person(lastname="Enrique",
          firstname="Luis"),), publish_year=2016, id=314)
        utils.create_book(librarian.db.session, br, self.admin_user)

        book = bookq.first()
        self.assertTrue(book is not None)

        # Ensure that it has contributors
        contribs = (librarian.db.session.query(BookContribution)
          .filter(BookContribution.book_id == book.id).all())

        self.assertTrue(len(contribs) > 0)
