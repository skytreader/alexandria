# -*- coding: utf-8 -*-
from base import AppTestCase
from faker import Faker
from librarian.models import BookContribution, Role
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
        #author_a1 = ContributorFactory()
        #translator_a1 = ContributorFactory()
        #illustrator_a1 = ContributorFactory()
        #illustrator_a2 = ContributorFactory()
        book_a = BookFactory()
        #self.session_add_all((author_a1, translator_a1, illustrator_a1,
        #  illustrator_a2, book_a))
        #librarian.db.session.flush()

        booka_author = BookContributionFactory(role=Role.get_preset_role("Author"),
          book=book_a)
        librarian.db.session.add(booka_author)
        booka_translator = BookContributionFactory(role=Role.get_preset_role("Translator"),
          book=book_a)
        librarian.db.session.add(booka_translator)
        booka_illus_1 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=book_a)
        librarian.db.session.add(booka_illus_1)
        librarian.db.session.commit()
        booka_illus_2 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=book_a)
        librarian.db.session.add(booka_illus_2)
        librarian.db.session.commit()

        #authors_a = [author_a1.make_plain_person()]
        #translators_a = [translator_a1.make_plain_person()]
        #illustrators_a = [illustrator_a1.make_plain_person(),
        #  illustrator_a2.make_plain_person()]
        #book_record_a = BookRecord(isbn=book_a.isbn, title=book_a.title,
        #  publisher=book_a.publisher.name, authors=authors_a,
        #  translators=translators_a, illustrators=illustrators_a)

        #author_b1 = ContributorFactory()
        #translator_b1 = ContributorFactory()
        #illustrator_b1 = ContributorFactory()
        #book_b = BookFactory()
        #self.session_add_all((author_b1, translator_b1, illustrator_b1, book_b))
        #librarian.db.session.flush()

        bookb_author = BookContributionFactory(role=Role.get_preset_role("Author"))
        bookb_translator = BookContributionFactory(role=Role.get_preset_role("Translator"))
        bookb_illus_1 = BookContributionFactory(role=Role.get_preset_role("Illustrator"))
        self.session_add_all((bookb_author, bookb_translator, bookb_illus_1))
        librarian.db.session.flush()
