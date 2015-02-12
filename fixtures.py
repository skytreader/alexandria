from app.models import Librarians, Roles
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        print "Existing instance %s for %s" % (str(kwargs), str(model))
        return instance
    else:
        print "New instance %s for %s" % (str(kwargs), str(model))
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()

    get_or_create(session, Librarians, username="admin", password="admin")
    
    roles = ("Author", "Illustrator", "Editor", "Translator")
    
    for r in roles:
        get_or_create(session, Roles, role_name=r, role_display="%s(s)" % r)