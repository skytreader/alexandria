# -*- coding: utf-8 -*-
from base import AppTestCase
from faker import Faker
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookFactory, ContributorFactory
from librarian.models import BookContribution

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
        author_a1 = ContributorFactory()
        translator_a1 = ContributorFactory()
        illustrator_a1 = ContributorFactory()
        illustrator_a2 = ContributorFactory()
        book_a = BookFactory()
        self.session_add_all((author_a1, translator_a1, illustrator_a1,
          illustrator_a2, book_a))
        librarian.db.session.flush()

        booka_author = BookContribution(book_id=book_a.id,
          role_id=self.ROLE_IDS["Author"], contributor_id=author_a1.id,
          creator_id=self.admin_user.id)
        booka_translator = BookContribution(book_id=book_a.id,
          role_id=self.ROLE_IDS["Translator"], contributor_id=translator_a1.id,
          creator_id=self.admin_user.id)
        booka_illus_1 = BookContribution(book_id=book_a.id,
          role_id=self.ROLE_IDS["Illustrator"], contributor_id=illustrator_a1.id,
          creator_id=self.admin_user.id)
        booka_illus_2 = BookContribution(book_id=book_a.id,
          role_id=self.ROLE_IDS["Illustrator"], contributor_id=illustrator_a2.id,
          creator_id=self.admin_user.id)
        self.session_add_all((booka_author, booka_translator, booka_illus_1,
          booka_illus_2))
