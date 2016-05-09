# -*- coding: utf-8 -*-
from factory.fuzzy import FuzzyText
from librarian.models import Book, Contributor, BookContribution
from librarian.tests.dummies import LibraryEntry
from librarian.tests.factories import (
  BookFactory, BookCompanyFactory, ContributorFactory,
)

import random
import re
import string

PROLLY_ROMAN_NUM = re.compile("^[%s]$" % (string.uppercase))
fuzzy_text = FuzzyText()

def make_name_object():
    return {"firstname": fuzzy_text.fuzz(), "lastname": fuzzy_text.fuzz()}

def create_library(session, admin, role_map, book_person_c=8, company_c=8, book_c=8,
  participant_c=8):
    """
    Create a library in the database with the given counts.

    Returns a list of `LibraryEntry` objects.
    """
    book_persons = [ContributorFactory() for _ in range(book_person_c)]
    printers = [BookCompanyFactory() for _ in range(company_c)]
    person_fns = [bp.firstname for bp in book_persons]

    for bp in book_persons:
        bp.creator_id = admin.id
        session.add(bp)

    for co in printers:
        co.creator_id = admin.id
        session.add(co)

    books = [BookFactory(publisher_id=random.choice(printers).id) for _ in range(book_c)]
    book_isbns = [b.isbn for b in books]

    for b in books:
        b.creator_id = admin.id
        session.add(b)

    session.commit()
    library = {}
    # Randomly assign persons to books as roles
    roles = role_map.keys()

    for _ in range(participant_c):
        rand_isbn = random.choice(book_isbns)
        rand_book = session.query(Book).filter(Book.isbn == rand_isbn).first()
        rand_person_fn = random.choice(person_fns)
        rand_person = session.query(Contributor).filter(Contributor.firstname == rand_person_fn).first()
        rand_role = random.choice(roles)
        _role = rand_role.lower()

        if library.get(rand_isbn):
            if library[rand_isbn].get(_role):
                library[rand_isbn][_role].append({"lastname": rand_person.lastname,
                  "firstname": rand_person.firstname})
            else:
                library[rand_isbn][_role] = [{"lastname": rand_person. lastname,
                  "firstname": rand_person.firstname},]

            bp = BookContribution(book_id=rand_book.id,
              contributor_id=rand_person.id, role_id=role_map[rand_role],
              creator_id=admin.id)
            session.add(bp)
            session.flush()
        else:
            library[rand_isbn] = {}
            library[rand_isbn]["title"] = rand_book.title
            library[rand_isbn][_role] = [{"lastname": rand_person.lastname,
              "firstname": rand_person.firstname}]
            library[rand_isbn]["publisher"] = rand_book.publisher

            book = session.query(Book).filter(Book.id == rand_book.id).first()
            bp = BookContribution(book_id=rand_book.id,
              contributor_id=rand_person.id, role_id=role_map[rand_role],
              creator_id=admin.id)
            session.add(bp)
            session.flush()

    session.commit()

    library_list = []

    for isbn in library.keys():
        book = library[isbn]
        book["isbn"] = isbn
        library_list.insert(0, LibraryEntry(**book))

    return library_list
