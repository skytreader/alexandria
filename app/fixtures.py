from flask.ext.sqlalchemy import SQLAlchemy
from models import Librarians, Roles

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        return instance

if __name__ == "__main__":
    session = SQLAlchemy()
    get_or_create(session, Librarians, {"username":"admin", "password":"admin"})
    
    roles = ("Author", "Illustrator", "Editor", "Translator")
    
    for r in roles:
        get_or_create(session, Roles, {"role_name":r, "role_display":"%s(s)" % r})
