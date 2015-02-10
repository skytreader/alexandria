from flask.ext.sqlalchemy import SQLAlchemy
from models import Librarians, Books

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        return instance

session = SQLAlchemy()
get_or_create(session, Librarians, {"username":"admin", "password":"admin"})
