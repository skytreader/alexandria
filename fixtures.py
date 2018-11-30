from librarian.models import get_or_create, Librarian, Role
from config import DefaultAlexandriaConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def insert_fixtures(session):
    admin_user = get_or_create(Librarian, session=session, will_commit=True,
      username="admin", password="admin", is_user_active=True, can_read=True,
      can_write=True, can_exec=True)
    
    roles = ("Author", "Illustrator", "Editor", "Translator")
    
    for r in roles:
        get_or_create(Role, session=session, will_commit=True, name=r,
          display_text="%s(s)" % r, creator=admin_user)

if __name__ == "__main__":
    engine = create_engine(DefaultAlexandriaConfig.SQLALCHEMY_DATABASE_URI, echo=True)
    session = sessionmaker(bind=engine)()

    insert_fixtures(session)
