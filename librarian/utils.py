# -*- coding: utf-8 -*-
import librarian
import re

ISBN_REGEX = re.compile("(\d{13}|\d{9}[\dX])")
NUMERIC_REGEX = re.compile("\d+")

 
class RequestData(object):
    
    def request_data(self):
        pass

class Person(RequestData):
    """
    Sometimes, you don't need a full Contributor object---i.e., you don't need
    the creation date for the record, just the first name and last name. This
    class is for that.
    """
    def __init__(self, lastname, firstname):
        self.lastname = lastname
        self.firstname = firstname

    def __eq__(self, p):
        return p.lastname == self.lastname and p.firstname == self.firstname

    def __hash__(self):
        return hash((self.lastname, self.firstname))
    
    def __str__(self):
        return self.lastname + ", " + self.firstname

    def __repr__(self):
        return str(self)

    def request_data(self):
        return '{"lastname": %s, "firstname": %s}' % (self.lastname, self.firstname)
        

class BookRecord(RequestData):
    """
    Class to consolidate DB records for easier listing. Each BookRecord instance
    consolidates the records of a single book.
    """
    
    def __init__(self, isbn, title, publisher, publish_year=None, author=None,
      translator=None, illustrator=None, editor=None):
        """
        Note that because language is a b*tch, the actual fields for the
        Person list parameters are accessible via their plural form (e.g.,
        whatever you gave for `author` is accessible via `self.author`).

        isbn: string
        title: string
        publisher: string
            The name of the publisher for this book.
        author: list of Person objects
        translator: list of Person objects
        illustrator: list of Person objects
        editor: list of Person objects
        """
        self.isbn = isbn
        self.title = title
        self.publisher = publisher
        self.publish_year = publish_year
        self.authors = frozenset(author if author else [])
        self.translators = frozenset(translator if translator else [])
        self.illustrators = frozenset(illustrator if illustrator else [])
        self.editors = frozenset(editor if editor else [])

    @staticmethod
    def make_hashable(dict_struct):
        """
        Takes a dictionary representation of this class and converts it to an
        actual instance of this class. For hashability.

        Note that because language is a b*tch, the keys pointing to the
        contributor list should be _singular_ form.
        """
        # Get each possible Contributor list and turn them into persons.
        auths = dict_struct.get("author")
        person_authors = [Person(**spam) for spam in auths] if auths else []
        trans = dict_struct.get("translator")
        person_translators = [Person(**spam) for spam in trans] if trans else []
        illus = dict_struct.get("illustrator")
        person_illustrators = [Person(**spam) for spam in illus] if illus else []
        edits = dict_struct.get("editor")
        person_editors = [Person(**spam) for spam in edits] if edits else []

        return BookRecord(isbn=dict_struct["isbn"], title=dict_struct["title"],
          publisher=dict_struct["publisher"], author=person_authors,
          translator=person_translators, illustrator=person_illustrators,
          editor=person_editors)

    def __eq__(self, br):
        return (self.isbn == br.isbn and self.title == br.title and
          self.publisher == br.publisher and self.authors == br.authors
          and self.translators == br.translators and
          self.illustrators == br.illustrators and self.editors == br.editors)

    def __hash__(self):
        return hash((self.isbn, self.title, self.publisher, self.authors,
          self.translators, self.illustrators, self.editors))

    def __str__(self):
        return str({"isbn": self.isbn, "title": self.title, "author": str(self.authors),
          "illustrator": str(self.illustrators), "editor": str(self.editors),
          "translator": str(self.translators), "publisher": str(self.publisher)})

    def request_data(self):
        def create_person_request_data(persons):
            return ", ".join([p.request_data() for p in persons])

        authors = create_person_request_data(self.authors)
        illustrators = create_person_request_data(self.illustrators)
        editors = create_person_request_data(self.editors)
        translators = create_person_request_data(self.translators)

        return {
            "isbn": self.isbn,
            "title": self.title,
            "authors": authors,
            "illustrators": illustrators,
            "editors": editors,
            "translators": translators,
            "publisher": self.publisher,
            "year": str(self.publish_year)
        }

    def __repr__(self):
        return str(self)

    @staticmethod
    def assembler(book_rows, as_obj=True):
        """
        Takes in rows from a SQL query with the columns in the following order:
    
        0 - Book.isbn
        1 - Book.title
        2 - Contributor.lastname
        3 - Contributor.firstname
        4 - Role.name
        5 - BookCompany.name
    
        And arranges them as an instance of this class.

        Return type will vary depending on the `as_obj` parameter but will
        essentially contain the same data in the same structure. If `as_obj`
        is True, return instances of this class. Otherwise, return maps.
        Note that maps are non-hashable but instances of this class is.
        """
        structured_catalog = {}
        
        for book in book_rows:
            record_exists = structured_catalog.get(book[0])
            role = book[4].lower()

            if record_exists:
                if structured_catalog[book[0]].get(role):
                    structured_catalog[book[0]][role].append(Person(lastname= book[2],
                      firstname=book[3]))
                else:
                    structured_catalog[book[0]][role] = [Person(lastname=book[2],
                      firstname=book[3])]
            else:
                fmt = {"title": book[1],
                  role: [Person(lastname=book[2], firstname=book[3])],
                  "publisher": book[5]}

                structured_catalog[book[0]] = fmt

        book_listing = []

        for isbn in structured_catalog.keys():
            book = structured_catalog[isbn]
            book["isbn"] = isbn
            br = BookRecord(**book)
            book_listing.insert(0, br)

        if not as_obj:
            book_listing = [book.__dict__ for book in book_listing]

        return book_listing

    @property
    def __dict__(self):
        base = {"isbn": self.isbn, "title": self.title, "publisher": self.publisher}
        base["author"] = [p.__dict__ for p in self.authors]
        base["translator"] = [p.__dict__ for p in self.translators]
        base["illustrator"] = [p.__dict__ for p in self.illustrators]
        base["editor"] = [p.__dict__ for p in self.editors]

        return base
    

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

class StatsDescriptor(object):
    """
    A collection of methods to give out an adjective depending on the value.
    The arguments are expected to be particular statistics. The method name
    reflects the statistic it tries to flavor.

    Each method returns a lowercase string of an English adjective.
    """

    @staticmethod
    def contrib_density(val):
        if 1 <= val < 2:
            return "focused"
        elif 2 <= val < 3:
            return "collaborative"
        else:
            return "spanning"

    @staticmethod
    def book_count(val):
        if val < 50:
            return "green"
        elif 50 <= val < 100:
            return "growing"
        elif 100 <= val < 200:
            return "substantial"
        elif 300 <= val < 400:
            return "voluminous"
        else:
            return "diverse"
