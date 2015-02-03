from app import db

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
