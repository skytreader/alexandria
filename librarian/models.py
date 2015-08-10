from flask.ext.login import UserMixin
from librarian import db, app
from librarian.errors import ConstraintError
from librarian.utils import isbn_check
from sqlalchemy.ext.declarative import declared_attr

"""
Year when ISBN was formalized.
"""
ISBN_START = 1970

"""
When the world ends according to the Long Now Foundation.
"""
LONG_NOW_WORLD_END = 99999


def get_or_create(model, will_commit=False, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        if will_commit:
            db.session.commit()
        return instance


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
      onupdate=db.func.current_timestamp())

class Librarian(Base, UserMixin):
    __tablename__ = "librarians"
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    can_read = db.Column(db.Boolean, nullable=False, default=False)
    can_write = db.Column(db.Boolean, nullable=False, default=False)
    can_exec = db.Column(db.Boolean, nullable=False, default=False)
    is_user_active = db.Column(db.Boolean, nullable=False, default=True)

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
    def creator(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.id"))

    @declared_attr
    def last_modifier(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.id"))

class Genre(UserTaggedBase):
    __tablename__ = "genres"
    name = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]

class Book(UserTaggedBase):
    __tablename__ = "books"
    isbn = db.Column(db.String(13), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.Integer, db.ForeignKey("genres.id"))
    printer = db.Column(db.Integer, db.ForeignKey("book_companies.id"))
    publisher = db.Column(db.Integer, db.ForeignKey("book_companies.id"))
    publish_year = db.Column(db.Integer, nullable=False, default=ISBN_START)

    def __init__(self, **kwargs):
        publish_year = int(kwargs["publish_year"])
        self.isbn = kwargs["isbn"]
        self.title = kwargs["title"]
        self.genre = kwargs["genre"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]
        self.printer = kwargs["printer"]
        self.publisher = kwargs["publisher"]
        
        # Check the publish year on ORM since not all SQL engines (mySQL, for
        # one), check constraints. Support the Long Now Foundation!!!
        pulish_year = int(kwargs["publish_year"])
        if ISBN_START <= publish_year and publish_year <= LONG_NOW_WORLD_END:
            self.publish_year = publish_year
        else:
            raise ConstraintError("bet. %d and %d" % (ISBN_START, LONG_NOW_WORLD_END),
              publish_year)

        if not isbn_check(self.isbn):
            raise ConstraintError("Invalid ISBN" , self.isbn)

class BookCompany(UserTaggedBase):
    """
    List?! List?! This is better off in NoSQL form!
    """
    __tablename__ = "book_companies"
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]

class Imprint(UserTaggedBase):
    __tablename__ = "imprints"
    mother_company = db.Column(db.Integer, db.ForeignKey("book_companies.id"))
    imprint_company = db.Column(db.Integer, db.ForeignKey("book_companies.id"))

    def __init__(self, **kwargs):
        self.mother_company = kwargs["mother_company"]
        self.imprint_company = kwargs["imprint_company"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]

class BookPerson(UserTaggedBase):
    __tablename__ = "book_persons"
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint("lastname", "firstname", name="uname"),)
    
    def __init__(self, **kwargs):
        self.lastname = kwargs["lastname"]
        self.firstname = kwargs["firstname"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]

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
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]

class BookParticipant(UserTaggedBase):
    """
    Consider that 99% of books will need the same roles over and over. 
    """
    __tablename__ = "book_participants"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    person_id = db.Column(db.Integer, db.ForeignKey("book_persons.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def __init__(self, **kwargs):
        self.book_id = kwargs["book_id"]
        self.person_id = kwargs["person_id"]
        self.role_id = kwargs["role_id"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]
    
    def __str__(self):
        return "Person %s worked on book %s as the role %s" % \
          (str(self.person_id), str(self.book_id), str(self.role_id))

class Pseudonym(UserTaggedBase):
    """
    Copied from original schema:

    Is this table ever going into any use?
    """
    __tablename__ = "pseudonyms"
    person_id = db.Column(db.Integer, db.ForeignKey("book_persons.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    # Pseudonyms are weird so only require the last!
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=True)

    def __init__(self, **kwargs):
        self.person_id = kwargs["person_id"]
        self.book_id = kwargs["book_id"]
        self.lastname = kwargs["lastname"]
        self.firstname = kwargs["firstname"]
        self.creator = kwargs["creator"]
        self.last_modifier = kwargs["creator"]
