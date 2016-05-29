# -*- coding: utf-8 -*-
from base import AppTestCase
from faker import Faker
from librarian.models import Book, BookCompany, BookContribution, Contributor, Role
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookContributionFactory, BookFactory, ContributorFactory
from librarian.utils import BookRecord

import unittest
import librarian
import librarian.utils

class IsbnTests(unittest.TestCase):
    
    def test_specified(self):
        isbn10_correct = "0306406152"
        isbn13_correct = "9780306406157"

        isbn10_incorrect = "0306406155"
        isbn13_incorrect = "9780306406155"

        self.assertTrue(librarian.utils.isbn_check(isbn10_correct))
        self.assertTrue(librarian.utils.isbn_check(isbn13_correct))
        self.assertFalse(librarian.utils.isbn_check(isbn10_incorrect))
        self.assertFalse(librarian.utils.isbn_check(isbn13_incorrect))
        
        self.assertFalse(librarian.utils.isbn_check("lettersabc"))
        self.assertFalse(librarian.utils.isbn_check("123456789"))

    def test_faker(self):
        fake = Faker()
        fake.add_provider(BookFieldsProvider)
        # dual-validation
        for i in range(100):
            self.assertTrue(librarian.utils.isbn_check(fake.isbn()))

        for i in range(100):
            self.assertTrue(librarian.utils.isbn_check(fake.isbn(False)))

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
          translator=booka_translators, illustrator=booka_illustrators)

        bookb_authors = [bookb_author.contributor.make_plain_person()]
        bookb_translators = [bookb_translator.contributor.make_plain_person()]
        bookb_illustrators = [bookb_illus.contributor.make_plain_person()]
        bookb_record = BookRecord(isbn=bookb.isbn, title=bookb.title,
          publisher=bookb.publisher.name, author=bookb_authors,
          translator=bookb_translators, illustrator=bookb_illustrators)

        expected_records = [booka_record, bookb_record]

        bookq = (librarian.db.session.query(Book.isbn, Book.title,
          Contributor.lastname, Contributor.firstname, Role.name,
          BookCompany.name)
          .filter(Book.id == BookContribution.book_id)
          .filter(BookContribution.contributor_id == Contributor.id)
          .filter(BookContribution.role_id == Role.id)
          .filter(Book.publisher_id == BookCompany.id))

        books = bookq.all()
        
        set(expected_records)
        self.assertEqual(set(expected_records), set(BookRecord.assembler(books)))
