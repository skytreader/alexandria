from app import db
from sqlalchemy.ext.declarative import declared_attr

class Base(db.Model):
    __abstract__ = True
    record_id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
      onupdate=db.func.current_timestamp())

class Librarians(Base):
    __tablename__ = "librarians"
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    can_read = db.Column(db.Boolean, nullable=False, default=False)
    can_write = db.Column(db.Boolean, nullable=False, default=False)
    can_exec = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username
    
    # TODO Actually implement these!
    # See https://flask-login.readthedocs.org/en/latest/
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.record_id

class UserTaggedBase(Base):
    """
    Those that will extend this class may take the convention that, upon creation,
    the last_modifier is the same as the creator.
    """
    __abstract__ = True

    @declared_attr
    def creator(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.record_id"))

    @declared_attr
    def last_modifier(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.record_id"))

class Genres(UserTaggedBase):
    __tablename__ = "genres"
    genre_name = db.Column(db.String(20), nullable=False)

    def __init__(self, genre_name):
        self.genre_name = genre_name

class Books(UserTaggedBase):
    __tablename__ = "books"
    isbn = db.Column(db.String(13), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.Integer, db.ForeignKey("genres.record_id"))

    def __init__(self, isbn, title, year, genre, creator):
        self.isbn = isbn
        self.title = title
        self.year = year
        self.genre = genre
        self.creator = creator
        self.last_modifier = creator

class BookCompanies(UserTaggedBase):
    """
    List?! List?! This is better off in NoSQL form!
    """
    __tablename__ = "book_companies"
    company_name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, company_name):
        self.company_name = company_name

class Imprints(UserTaggedBase):
    __tablename__ = "imprints"
    mother_company = db.Column(db.Integer, db.ForeignKey("book_companies.record_id"))
    imprint_company = db.Column(db.Integer, db.ForeignKey("book_companies.record_id"))

    def __init__(self, mother_company, imprint_company):
        self.mother_company = mother_company
        self.imprint_company = imprint_company

class BookPersons(UserTaggedBase):
    __tablename__ = "book_persons"
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    
    def __init__(self, lastname, firstname):
        self.lastname = lastname
        self.firstname = firstname

class Roles(UserTaggedBase):
    """
    The purpose of this table is to enumerate the contributions we are interested
    in for the books.

    The role_name is for the actual contribution we are interested in while
    role_display is for how it is prompted for in the app's forms.
    """
    __tablename__ = "roles"
    role_name = db.Column(db.String(255), unique=True, nullable=False)
    role_display = db.Column(db.String(255), nullable=False)

    def __init__(self, role_name, role_display):
        self.role_name = role_name
        self.role_display = role_display

class BookParticipants(UserTaggedBase):
    """
    Consider that 99% of books will need the same roles over and over. 
    """
    __tablename__ = "book_participants"
    book_id = db.Column(db.Integer, db.ForeignKey("books.record_id"))
    person_id = db.Column(db.Integer, db.ForeignKey("book_persons.record_id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.record_id"))

    def __init__(self, book_id, person_id, role_id):
        book_id = book_id
        person_id = person_id
        role_id = role_id

class Pseudonyms(UserTaggedBase):
    """
    Copied from original schema:

    Is this table ever going into any use?
    """
    __tablename__ = "pseudonyms"
    person_id = db.Column(db.Integer, db.ForeignKey("book_persons.record_id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.record_id"))
    # Pseudonyms are weird so only require the last!
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=True)

    def __init__(self, person_id, book_id, lastname, firstname):
        self.person_id = person_id
        self.book_id = book_id
        self.lastname = lastname
        self.firstname = firstname
