from app import db, app
from sqlalchemy.ext.declarative import declared_attr

def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance


class Base(db.Model):
    __abstract__ = True
    record_id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
      onupdate=db.func.current_timestamp())

class Librarian(Base):
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

class Genre(UserTaggedBase):
    __tablename__ = "genres"
    genre_name = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, genre_name, creator):
        self.genre_name = genre_name
        self.creator = creator
        self.last_modifier = creator

class Book(UserTaggedBase):
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

class BookCompany(UserTaggedBase):
    """
    List?! List?! This is better off in NoSQL form!
    """
    __tablename__ = "book_companies"
    company_name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, company_name, creator):
        self.company_name = company_name
        self.creator = creator
        self.last_modifier = creator

class Imprint(UserTaggedBase):
    __tablename__ = "imprints"
    mother_company = db.Column(db.Integer, db.ForeignKey("book_companies.record_id"))
    imprint_company = db.Column(db.Integer, db.ForeignKey("book_companies.record_id"))

    def __init__(self, mother_company, imprint_company, creator):
        self.mother_company = mother_company
        self.imprint_company = imprint_company
        self.creator = creator
        self.last_modifier = creator

class BookPerson(UserTaggedBase):
    __tablename__ = "book_persons"
    lastname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint("lastname", "firstname", name="uname"),)
    
    def __init__(self, lastname, firstname, creator):
        self.lastname = lastname
        self.firstname = firstname
        self.creator = creator
        self.last_modifier = creator

class Role(UserTaggedBase):
    """
    The purpose of this table is to enumerate the contributions we are interested
    in for the books.

    The role_name is for the actual contribution we are interested in while
    role_display is for how it is prompted for in the app's forms.
    """
    __tablename__ = "roles"
    role_name = db.Column(db.String(255), unique=True, nullable=False)
    role_display = db.Column(db.String(255), nullable=False)

    def __init__(self, role_name, role_display, creator):
        self.role_name = role_name
        self.role_display = role_display
        self.creator = creator
        self.last_modifier = creator

class BookParticipant(UserTaggedBase):
    """
    Consider that 99% of books will need the same roles over and over. 
    """
    __tablename__ = "book_participants"
    book_id = db.Column(db.Integer, db.ForeignKey("books.record_id"))
    person_id = db.Column(db.Integer, db.ForeignKey("book_persons.record_id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.record_id"))

    def __init__(self, book_id, person_id, role_id, creator):
        self.book_id = book_id
        self.person_id = person_id
        self.role_id = role_id
        self.creator = creator
        self.last_modifier = creator
    
    def __str__(self):
        return "Person %s worked on book %s as the role %s" % \
          (str(self.person_id), str(self.book_id), str(self.role_id))

class Pseudonym(UserTaggedBase):
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

    def __init__(self, person_id, book_id, lastname, firstname, creator):
        self.person_id = person_id
        self.book_id = book_id
        self.lastname = lastname
        self.firstname = firstname
        self.creator = creator
        self.last_modifier = creator
