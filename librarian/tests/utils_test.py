# -*- coding: utf-8 -*-
from faker import Faker
from librarian.tests.fakers import BookFieldsProvider

import unittest
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
