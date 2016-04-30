# -*- coding: utf-8 -*-
from flask.ext.login import current_user, UserMixin
from librarian import app, cache, db
from librarian.errors import ConstraintError
from librarian.utils import isbn_check
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

import config

"""
Year when ISBN was formalized.
"""
ISBN_START = 1970

"""
When the world ends according to the Long Now Foundation.
"""
LONG_NOW_WORLD_END = 99999


def get_or_create(model, will_commit=False, **kwargs):
    """
    Get the record from the table represented by the given model which
    corresponds to **kwargs.

    In **kwargs, there is no need to specify the creator of the record; it
    does not make sense to ask for it given that it might've been created by
    another user. If it is given as a parameter, it will be ignored in the
    "get" part of this method.

    If the logic falls to the creation of a new record, the creator will be set
    as the current user. If no user is logged-in when this is called, the admin
    user is used.
    """
    given_creator = kwargs.pop("creator_id", None)
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        if given_creator:
            kwargs["creator_id"] = given_creator
        else:
            admin = (db.session.query(Librarian)
              .filter(Librarian.username=='admin').first())
            kwargs["creator_id"] = admin.id

        instance = model(**kwargs)
        if will_commit:
            db.session.add(instance)
            db.session.commit()
        return instance


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp(),
      server_default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
      server_default=db.func.current_timestamp(),
      onupdate=db.func.current_timestamp())

class Librarian(Base, UserMixin):
    __tablename__ = "librarians"
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    can_read = db.Column(db.Boolean, nullable=False, default=False,
      server_default=db.false())
    can_write = db.Column(db.Boolean, nullable=False, default=False,
      server_default=db.false())
    can_exec = db.Column(db.Boolean, nullable=False, default=False,
      server_default=db.false())
    is_user_active = db.Column(db.Boolean, nullable=False, default=True,
      server_default=db.true())

    def __init__(self, **kwargs):
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.can_read = kwargs.get("can_read", False)
        self.can_write = kwargs.get("can_write", False)
        self.can_exec = kwargs.get("can_exec", False)
        self.is_user_active = kwargs.get("is_user_active", True)

    def __repr__(self):
        return self.username
    
    def get_id(self):
        return self.id


class UserTaggedBase(Base):
    """
    Those that will extend this class may take the convention that, upon creation,
    the last_modifier is the same as the creator.
    """
    __abstract__ = True

    @declared_attr
    def creator_id(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.id"))

    @declared_attr
    def last_modifier_id(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.id"))

class Genre(UserTaggedBase):
    __tablename__ = "genres"
    name = db.Column(db.String(40), nullable=False, unique=True)
    creator = relationship("Librarian", foreign_keys="Genre.creator_id")
    last_modifier = relationship("Librarian", foreign_keys="Genre.last_modifier_id")

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

class Book(UserTaggedBase):
    __tablename__ = "books"
    isbn = db.Column(db.String(13), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id",
      name="book_genre_fk"))
    publisher_id = db.Column(db.Integer, db.ForeignKey("book_companies.id",
      name="book_book_company_fk1"))
    publish_year = db.Column(db.Integer, nullable=False, default=ISBN_START,
      server_default=str(ISBN_START))

    genre = relationship("Genre")
    publisher = relationship("BookCompany")

    def __init__(self, **kwargs):
        if not isbn_check(kwargs["isbn"]):
            raise ConstraintError("Invalid ISBN" , self.isbn)

        self.publish_year = int(kwargs["publish_year"])
        self.isbn = kwargs["isbn"]
        self.title = kwargs["title"]
        self.genre = kwargs["genre"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]
        self.printer = kwargs["printer"]
        self.publisher = kwargs["publisher"]

class BookCompany(UserTaggedBase):
    """
    List?! List?! This is better off in NoSQL form!
    """
    __tablename__ = "book_companies"
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

class Imprint(UserTaggedBase):
    __tablename__ = "imprints"
    mother_company_id = db.Column(db.Integer, db.ForeignKey("book_companies.id",
      name="imprint_book_company_fk1"))
    imprint_company_id = db.Column(db.Integer, db.ForeignKey("book_companies.id",
      name="imprint_book_company_fk2"))
    
    mother_company = relationship("BookCompany", foreign_keys="Imprint.mother_company_id")
    #mother_company = relationship("BookCompany")
    imprint_company = relationship("BookCompany", foreign_keys="Imprint.imprint_company_id")
    #imprint_company = relationship("BookCompany")

    def __init__(self, **kwargs):
        self.mother_company_id = kwargs["mother_company"]
        self.imprint_company_id = kwargs["imprint_company"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

class Contributor(UserTaggedBase):
    __tablename__ = "contributors"
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint("lastname", "firstname", name="uname"),)
    
    def __init__(self, **kwargs):
        self.lastname = kwargs["lastname"]
        self.firstname = kwargs["firstname"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

    def __str__(self):
        return str({"id": self.id, "lastname": self.lastname, "firstname": self.firstname})

class Role(UserTaggedBase):
    """
    The purpose of this table is to enumerate the contributions we are interested
    in for the books.

    The name is for the actual contribution we are interested in while
    display_text is for how it is prompted for in the app's forms.
    """
    __tablename__ = "roles"
    name = db.Column(db.String(255), unique=True, nullable=False)
    display_text = db.Column(db.String(255), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.display_text = kwargs["display_text"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

    @staticmethod
    @cache.memoize(config.CACHE_TIMEOUT)
    def get_preset_role(role_name):
        role = Role.query.filter_by(name=role_name).first()
        return role
        

class BookContribution(UserTaggedBase):
    """
    Consider that 99% of books will need the same roles over and over. 
    """
    __tablename__ = "book_contributions"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id",
      name="book_participant_book_fk1"))
    contributor_id = db.Column(db.Integer, db.ForeignKey("contributors.id",
      name="book_participant_book_person_fk1"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id",
      name="book_pariticipant_role_fk1"))

    book = relationship("Book")
    contributor = relationship("Contributor")
    role = relationship("Role")

    def __init__(self, **kwargs):
        self.book_id = kwargs["book_id"]
        self.person_id = kwargs["person_id"]
        self.role_id = kwargs["role_id"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]
    
    def __str__(self):
        return "Person %s worked on book %s as the role %s" % \
          (str(self.person_id), str(self.book_id), str(self.role_id))

class Printer(UserTaggedBase):
    __tablename__ = "printers"
    company_id = db.Column(db.Integer, db.ForeignKey("book_companies.id",
      name="printer_book_company_fk1"), primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id",
      name="printer_book_fk1"), primary_key = True)

    company = relationship("BookCompany")
    book = relationship("Book")

    def __init__(self, **kwargs):
        self.book_id = kwargs["book_id"]
        self.company_id = kwargs["company_id"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]

class Pseudonym(UserTaggedBase):
    """
    Copied from original schema:

    Is this table ever going into any use?
    """
    __tablename__ = "pseudonyms"
    person_id = db.Column(db.Integer, db.ForeignKey("contributors.id",
      name="pseudonym_book_person_fk1"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id",
      name="pseudonym_book_fk1"))
    # Pseudonyms are weird so only require the last!
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=True)

    person = relationship("Contributor")
    book = relationship("Book")

    def __init__(self, **kwargs):
        self.person_id = kwargs["person_id"]
        self.book_id = kwargs["book_id"]
        self.lastname = kwargs["lastname"]
        self.firstname = kwargs["firstname"]
        self.creator_id = kwargs["creator_id"]
        self.last_modifier_id = kwargs["creator_id"]
