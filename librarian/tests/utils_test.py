# -*- coding: utf-8 -*-
from base import AppTestCase
from faker import Faker
from librarian.errors import ConstraintError
from librarian.models import Book, BookCompany, BookContribution, Contributor, Role
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.factories import BookContributionFactory, BookFactory, ContributorFactory
from librarian.tests import utils
from librarian.utils import BookRecord, compute_isbn10_checkdigit, compute_isbn13_checkdigit, has_equivalent_isbn, isbn_check, Person

import copy
import unittest
import librarian
import random
import string

fake = Faker()
fake.add_provider(BookFieldsProvider)

class IsbnTests(unittest.TestCase):
    
    def test_specified(self):
        isbn10_correct = "0306406152"
        isbn13_correct = "9780306406157"

        isbn10_incorrect = "0306406155"
        isbn13_incorrect = "9780306406155"

        self.assertTrue(isbn_check(isbn10_correct))
        self.assertTrue(isbn_check("0843610727"))
        self.assertTrue(isbn_check(isbn13_correct))
        self.assertFalse(isbn_check(isbn10_incorrect))
        self.assertFalse(isbn_check(isbn13_incorrect))
        
        self.assertFalse(isbn_check("lettersabc"))
        self.assertFalse(isbn_check("123456789"))

    def test_faker(self):
        # dual-validation
        for i in range(100):
            self.assertTrue(isbn_check(fake.isbn()))

        for i in range(100):
            self.assertTrue(isbn_check(fake.isbn(False)))

    def test_compute_isbn10_checkdigit(self):
        self.assertEqual('2', compute_isbn10_checkdigit("030640615"))
        self.assertRaises(ConstraintError, compute_isbn10_checkdigit, "978030640615")
        self.assertRaises(ConstraintError, compute_isbn10_checkdigit, "abcdefghi")

        for i in range(100):
            partial_isbn = "".join([random.choice(string.digits) for _ in range(9)])
            self.assertEqual(1, len(compute_isbn10_checkdigit(partial_isbn)))

    def test_compute_isbn13_checkdigit(self):
        self.assertEqual('7', compute_isbn13_checkdigit("978030640615"))
        self.assertRaises(ConstraintError, compute_isbn13_checkdigit, "030640615")
        self.assertRaises(ConstraintError, compute_isbn13_checkdigit, "abcdefghijkl")

        for i in range(100):
            partial_isbn = "".join([random.choice(string.digits) for _ in range(12)])
            self.assertEqual(1, len(compute_isbn13_checkdigit(partial_isbn)))

    def test_has_equivalent_isbn_10to13(self):
        saturday = BookFactory(isbn="0099497166", title="Saturday")
        librarian.db.session.add(saturday)
        librarian.db.session.flush()

        self.assertTrue(has_equivalent_isbn("9780099497165"))

    def test_has_equivalent_isbn_13to10(self):
        saturday = BookFactory(isbn="9780099497165", title="Saturday")
        librarian.db.session.add(saturday)
        librarian.db.session.flush()

        self.assertTrue(has_equivalent_isbn("0099497166"))

class BookRecordTests(AppTestCase):
    
    def test_assembler(self):
        # Create the DB records
        booka = BookFactory()
        #r = Role(name="administrator", creator=self.admin_user, display_text="Administrator")
        r = Role.get_preset_role("Illustrator")
        librarian.db.session.add(booka)
        librarian.db.session.flush()

        authora = Contributor(firstname="Arthur", lastname="McAuthor", creator=self.admin_user)
        translatora = Contributor(firstname="Terrence", lastname="McTranslator", creator=self.admin_user)
        illus1a = Contributor(firstname="Illy I", lastname="McIllustrator", creator=self.admin_user)
        illus2a = Contributor(firstname="Illy II", lastname="McIllustrator", creator=self.admin_user)
        librarian.db.session.add_all((
            authora, translatora, illus1a, illus2a
        ))
        librarian.db.session.flush()

        booka_author = BookContribution(
            book=booka, contributor=authora, creator=self.admin_user,
            role=Role.get_preset_role("Author")
        )
        booka_translator = BookContribution(
            book=booka, contributor=translatora, creator=self.admin_user,
            role=Role.get_preset_role("Translator")
        )
        booka_illus1 = BookContribution(
            book=booka, contributor=illus1a, creator=self.admin_user,
            #role=Role.get_preset_role("Illustrator")
            role=r
        )
        booka_illus2 = BookContribution(
            book=booka, contributor=illus2a, creator=self.admin_user,
            #role=Role.get_preset_role("Illustrator")
            role=r
        )
        #librarian.db.session.add_all((
        #    booka_author, booka_translator, booka_illus1, booka_illus2
        #))
        librarian.db.session.add(booka_author)
        librarian.db.session.add(booka_translator)
        librarian.db.session.add(booka_illus1)
        librarian.db.session.add(booka_illus2)

        #booka_author = BookContributionFactory(role=Role.get_preset_role("Author"),
        #  book=booka, creator=self.admin_user)
        #librarian.db.session.add(booka_author)
        #booka_translator = BookContributionFactory(role=Role.get_preset_role("Translator"),
        #  book=booka, creator=self.admin_user)
        #librarian.db.session.add(booka_translator)
        #booka_illus1 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
        #  book=booka, creator=self.admin_user)
        #librarian.db.session.add(booka_illus1)
        #librarian.db.session.commit()
        #booka_illus2 = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
        #  book=booka, creator=self.admin_user)
        #librarian.db.session.add(booka_illus2)
        librarian.db.session.commit()

        bookb = BookFactory()
        bookb_author = BookContributionFactory(role=Role.get_preset_role("Author"),
          book=bookb, creator=self.admin_user)
        bookb_translator = BookContributionFactory(role=Role.get_preset_role("Translator"),
          book=bookb, creator=self.admin_user)
        bookb_illus = BookContributionFactory(role=Role.get_preset_role("Illustrator"),
          book=bookb, creator=self.admin_user)
        self.session_add_all((bookb_author, bookb_translator, bookb_illus))
        librarian.db.session.flush()

        # Create the BookRecord objects
        booka_authors = [booka_author.contributor.make_plain_person()]
        booka_translators = [booka_translator.contributor.make_plain_person()]
        booka_illustrators = [booka_illus1.contributor.make_plain_person(),
          booka_illus2.contributor.make_plain_person()]
        booka_record = BookRecord(
            isbn=booka.isbn, title=booka.title, publisher=booka.publisher.name,
            author=booka_authors, translator=booka_translators,
            illustrator=booka_illustrators, id=booka.id, genre="Test")

        bookb_authors = [bookb_author.contributor.make_plain_person()]
        bookb_translators = [bookb_translator.contributor.make_plain_person()]
        bookb_illustrators = [bookb_illus.contributor.make_plain_person()]
        bookb_record = BookRecord(
            isbn=bookb.isbn, title=bookb.title, publisher=bookb.publisher.name,
            author=bookb_authors, translator=bookb_translators,
            illustrator=bookb_illustrators, id=bookb.id, genre="Test")

        expected_records = [booka_record, bookb_record]

        books = BookRecord.base_assembler_query().all()
        
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

    def test_factory(self):
        title = "World Taekwondo Federation Welterweight"
        publisher_name="International Olympic Committee"
        self.verify_does_not_exist(Book, title=title)
        self.verify_does_not_exist(Contributor, lastname="Tazegul", firstname="Servet")
        self.verify_does_not_exist(BookCompany, name=publisher_name)
        factory_made = BookRecord.factory(
            isbn=fake.isbn(), title=title, publisher=publisher_name,
            author=[Person("Tazegul", "Servet")], genre="Sports", publish_year=2017
        )
        self.verify_inserted(Book, title=title)
        self.verify_inserted(Contributor, lastname="Tazegul", firstname="Servet")
        self.verify_inserted(BookCompany, name=publisher_name)

        self.assertTrue(factory_made is not None)
        self.assertTrue(factory_made.id is not None)

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
        br = BookRecord(
            isbn=sample_isbn, title="Another Chance for Poland",
            publisher="Eurosport", author=(Person(lastname="Enrique",
            firstname="Luis"),), publish_year=2016, id=314, genre="Test"
        )
        utils.create_book(librarian.db.session, br, self.admin_user)

        book = bookq.first()
        self.assertTrue(book is not None)

        # Ensure that it has contributors
        contribs = (librarian.db.session.query(BookContribution)
          .filter(BookContribution.book_id == book.id).all())

        self.assertTrue(len(contribs) > 0)
