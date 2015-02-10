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
    __abstract__ = True
    #last_modifier = db.Column(db.Integer, db.ForeignKey("librarians.record_id"))

    @declared_attr
    def creator(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.record_id"))

    @declared_attr
    def last_modifier(self):
        return db.Column(db.Integer, db.ForeignKey("librarians.record_id"))

class Books(UserTaggedBase):
    __tablename__ = "books"
    isbn = db.Column(db.String(13), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
