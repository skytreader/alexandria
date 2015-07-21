from librarian.models import Librarian, Role
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
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    session = sessionmaker(bind=engine)()

    admin_user = get_or_create(session, Librarian, username="admin", password="admin", is_user_active=True, can_read=True, can_write=True, can_exec=True)
    
    roles = ("Author", "Illustrator", "Editor", "Translator")
    
    for r in roles:
        get_or_create(session, Role, role_name=r, role_display="%s(s)" % r,
          creator=admin_user.record_id)
