from librarian.models import get_or_create, Librarian, Role
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    session = sessionmaker(bind=engine)()

    admin_user = get_or_create(Librarian, True, username="admin",
      password="admin", is_user_active=True, can_read=True, can_write=True,
      can_exec=True)
    
    roles = ("Author", "Illustrator", "Editor", "Translator")
    
    for r in roles:
        get_or_create(Role, will_commit=True, name=r, display_text="%s(s)" % r,
          creator=admin_user.id)
