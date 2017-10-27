# -*- coding: utf-8 -*-

from librarian import app, db

import config
import copy
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
        return '{"lastname": "%s", "firstname": "%s"}' % (self.lastname, self.firstname)

    def __deepcopy__(self, memo):
        return Person(lastname=self.lastname, firstname=self.firstname)

class BookRecord(RequestData):
    """
    Class to consolidate DB records for easier listing. Each BookRecord instance
    consolidates the records of a single book.
    """

    """
    When an instance of this class is converted to a dictionary, the following
    fields will hold lists.
    """
    LIST_TYPES = ["author", "translator", "illustrator", "editor"]

    @staticmethod
    def base_assembler_query():
        """
        Use this when the results of your query is meant to be assembled via
        BookRecord.assembler. This is just a query that enumerates the result set
        as expected by BookRecord.assembler. Filter as necessary.
        """
        from librarian.models import Book, BookCompany, BookContribution, Contributor, Role, Genre
        return (
            db.session.query(
                Book.id, Book.isbn, Book.title, Contributor.lastname,
                Contributor.firstname, Role.name, BookCompany.name, Genre.name,
                Book.publish_year
            ).filter(Book.id == BookContribution.book_id)
            .filter(BookContribution.contributor_id == Contributor.id)
            .filter(BookContribution.role_id == Role.id)
            .filter(Book.publisher_id == BookCompany.id)
            .filter(Book.genre_id == Genre.id)
        )
    
    def __init__(
        self, isbn, title, publisher, publish_year=None, author=None,
        translator=None, illustrator=None, editor=None, genre=None, id=None,
        printer=None
     ):
        """
        Note that because language is a b*tch, the actual fields for the
        Person list parameters are accessible via their plural form (e.g.,
        whatever you gave for `author` is accessible via `self.author`).

        id: integer
            The book id.
        isbn: string
        title: string
        publisher: string
            The name of the publisher for this book.
        author: list of Person objects
        translator: list of Person objects
        illustrator: list of Person objects
        editor: list of Person objects
        genre: string
        """
        self.id = id
        self.isbn = isbn
        self.title = title
        self.printer = printer
        self.publisher = publisher
        self.publish_year = publish_year
        self.authors = frozenset(author if author else [])
        self.translators = frozenset(translator if translator else [])
        self.illustrators = frozenset(illustrator if illustrator else [])
        self.editors = frozenset(editor if editor else [])
        self.genre = genre

    @classmethod
    def factory(
        cls, isbn, title, publisher, publish_year=None, author=None,
        translator=None, illustrator=None, editor=None, genre=None,
        printer=None
    ):
        """
        This method adds all created models to the session and returns an
        instance of this class collating the models created.
        """

        import librarian.tests.factories as AppFactories
        from librarian.models import Role
        def contributor_factory(person_list):
            """
            Adds all Persons to the session as Contributors. Returns a list of
            the Contributors created.
            """
            contribs = []
            if person_list:
                for person in person_list:
                    contrib = AppFactories.ContributorFactory(
                        lastname=person.lastname, firstname=person.firstname
                    )
                    contribs.insert(0, contrib)
                    db.session.add(contrib)

            return contribs

        def book_contribution_factory(book, contributors, role):
            for contrib in contributors:
                db.session.add(AppFactories.BookContributionFactory(
                    book=book, contributor=contrib, role=role
                ))

        book = AppFactories.BookFactory(
            isbn=isbn, title=title, genre=AppFactories.GenreFactory(name=genre),
            publisher=AppFactories.BookCompanyFactory(name=publisher), publish_year=publish_year
        )
        db.session.add(book)

        book_contribution_factory(book, contributor_factory(author), Role.get_preset_role("Author"))
        book_contribution_factory(book, contributor_factory(translator), Role.get_preset_role("Translator"))
        book_contribution_factory(book, contributor_factory(illustrator), Role.get_preset_role("Illustrator"))
        book_contribution_factory(book, contributor_factory(editor), Role.get_preset_role("Editor"))

        db.session.flush()

        return cls(
            isbn, title, publisher, publish_year, author, translator,
            illustrator, editor, genre, book.id, printer
        )

    def __deepcopy__(self, memo):
        # Create record first then set authors later because constructors expect
        # lists while actual fields are frozensets.
        record = BookRecord(isbn=self.isbn, title=self.title,
          publisher=self.publisher, publish_year=self.publish_year,
          genre=self.genre, id=self.id, printer=self.printer)

        record.authors = copy.deepcopy(self.authors)
        record.translators = copy.deepcopy(self.translators)
        record.illustrators = copy.deepcopy(self.illustrators)
        record.editors = copy.deepcopy(self.editors)

        return record

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
          editor=person_editors, id=dict_struct["id"],
          printer=dict_struct["printer"])

    def __eq__(self, br):
        return (self.isbn == br.isbn and self.title == br.title and
          self.publisher == br.publisher and self.authors == br.authors
          and self.translators == br.translators and
          self.illustrators == br.illustrators and self.editors == br.editors
          and self.id == br.id and self.printer == br.printer)

    def __hash__(self):
        return hash((self.isbn, self.title, self.publisher, self.authors,
          self.translators, self.illustrators, self.editors))

    def __str__(self):
        return str({"isbn": self.isbn, "title": self.title, "author": str(self.authors),
          "illustrator": str(self.illustrators), "editor": str(self.editors),
          "translator": str(self.translators), "publisher": str(self.publisher),
          "printer": str(self.printer), "id": self.id})

    def request_data(self):
        def create_person_request_data(persons):
            return "[%s]" % ", ".join([p.request_data() for p in persons])

        authors = create_person_request_data(self.authors)
        illustrators = create_person_request_data(self.illustrators)
        editors = create_person_request_data(self.editors)
        translators = create_person_request_data(self.translators)

        return {
            "book_id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "authors": authors,
            "illustrators": illustrators,
            "editors": editors,
            "translators": translators,
            "printer": self.printer,
            "publisher": self.publisher,
            "year": str(self.publish_year),
            "genre": self.genre
        }

    def __repr__(self):
        return str(self)

    @staticmethod
    def assembler(book_rows, as_obj=True):
        """
        Takes in rows from a SQL query with the columns in the following order:
    
        0 - Book.id
        1 - Book.isbn
        2 - Book.title
        3 - Contributor.lastname
        4 - Contributor.firstname
        5 - Role.name
        6 - BookCompany.name
        7 - Genre.name
        8 - Book.publish_year
    
        And arranges them as an instance of this class. Returned as a ist.

        Type of list items will vary depending on the `as_obj` parameter but will
        essentially contain the same data in the same structure. If `as_obj`
        is True, return instances of this class. Otherwise, return maps.
        Note that maps are non-hashable but instances of this class is.
        """
        structured_catalog = {}
        
        for (
            id, isbn, title, contrib_lastname, contrib_firstname, role,
            publisher, genre, publish_year
        ) in book_rows:
            record_exists = structured_catalog.get(isbn)
            role = role.lower()

            if record_exists:
                if structured_catalog[isbn].get(role):
                    structured_catalog[isbn][role].append(Person(
                      lastname=contrib_lastname, firstname=contrib_firstname))
                else:
                    structured_catalog[isbn][role] = [Person(
                      lastname=contrib_lastname, firstname=contrib_firstname)]
            else:
                fmt = {"title": title, "id": id, "genre": genre,
                  role: [Person(lastname=contrib_lastname, firstname=contrib_firstname)],
                  "publisher": publisher, "publish_year": publish_year}

                structured_catalog[isbn] = fmt

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
        base = {"isbn": self.isbn, "title": self.title, "genre": self.genre,
          "publisher": self.publisher, "id": self.id, "printer": self.printer,
          "year": self.publish_year}
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
        if val < 1:
            return "low"
        elif 1 <= val < 2:
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
