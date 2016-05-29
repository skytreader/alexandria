# -*- coding: utf-8 -*-
import librarian
import re

ISBN_REGEX = re.compile("(\d{13}|\d{9}[\dX])")
NUMERIC_REGEX = re.compile("\d+")

 
class Person(object):
    def __init__(self, lastname, firstname):
        self.lastname = lastname
        self.firstname = firstname

    def __eq__(self, p):
        return p.lastname == self.lastname and p.firstname == self.firstname

    def __hash__(self):
        return hash((self.lastname, self.firstname))
    
    def __str__(self):
        return self.lastname + ", " + self.firstname
        

class BookRecord(object):
    """
    Class to consolidate DB records for easier listing. Each BookRecord instance
    consolidates the records of a single book.
    """
    
    def __init__(self, isbn, title, publisher, authors=None, translators=None,
      illustrators=None, editors=None):
        """
        isbn: string
        title: string
        publisher: string
            The name of the publisher for this book.
        authors: list of Person objects
        translators: list of Person objects
        illustrators: list of Person objects
        editors: list of Person objects
        """
        self.isbn = isbn
        self.title = title
        self.publisher = publisher
        self.authors = frozenset(authors if authors else [])
        self.translators = frozenset(translators if translators else [])
        self.illustrators = frozenset(illustrators if illustrators else [])
        self.editors = frozenset(editors if editors else [])

    def __eq__(self, br):
        return (self.isbn == br.isbn and self.title == br.title and
          self.publisher == br.publisher and set(self.authors) == set(br.authors)
          and set(self.translators) == set(br.translators) and
          set(self.illustrators) == set(br.illustrators) and
          set(self.editors) == set(br.illustrators))

    def __hash__(self):
        return hash((self.isbn, self.title, self.publisher, self.authors,
          self.translators, self.illustrators, self.editors))

    @staticmethod
    def assembler(book_rows):
        """
        Takes in rows from a SQL query with the columns in the following order:
    
        0 - Book.isbn
        1 - Book.title
        2 - Contributor.lastname
        3 - Contributor.firstname
        4 - Role.name
        5 - BookCompany.name
    
        And arranges them as an instance of this class.

        Returns a list of instances of this class
        """
        structured_catalog = {}
        
        for book in book_rows:
            record_exists = structured_catalog.get(book[0])
            role = book[4].lower()

            if record_exists:
                if structured_catalog[book[0]].get(role):
                    structured_catalog[book[0]][role].append({"lastname": book[2],
                      "firstname": book[3]})
                else:
                    structured_catalog[book[0]][role] = [{"lastname": book[2],
                      "firstname": book[3]}]
            else:
                fmt = {"title": book[1],
                  role: [{"lastname": book[2], "firstname": book[3]}],
                  "publisher": book[5]}

                structured_catalog[book[0]] = fmt

        book_listing = []

        for isbn in structured_catalog.keys():
            book = structured_catalog[isbn]
            book["isbn"] = isbn
            book_listing.insert(0, book)

        print "return type", type(book_listing)
        return book_listing


def isbn_check(isbn):
    """
    Checks for the valididty of the given ISBN string and returns a boolean to
    indicate validity. If the given string is not exactly either of length 10 or
    13, raise ConstraintError.
    """
    if ISBN_REGEX.match(isbn):
        if len(isbn) == 10:
            check = 0

            for idx, d in enumerate(isbn):
                if d == 'X':
                    # because should only happen at the last digit
                    check += 100
                    continue

                check += int(d) * (idx + 1)

            return (check % 11) == 0
        else:
            check = 0
            
            for idx, d in enumerate(isbn):
                if idx % 2:
                    check += 3 * int(d)
                else:
                    check += int(d)

            return (check % 10) == 0

    return False

def route_exists(route):
    return route in map(lambda r: r.rule, librarian.app.url_map.iter_rules())

def stats_adjective(val):
    if 1 <= val < 2:
        return "focused"
    elif 2 <= val < 3:
        return "collaborative"
    else:
        return "diverse"
