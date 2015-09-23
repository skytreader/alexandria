from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("DELETE FROM librarians;")
    engine.execute("DELETE FROM roles;")
    engine.execute("DELETE FROM genres;")
    engine.execute("DELETE FROM books;")
    engine.execute("DELETE FROM book_companies;")
    engine.execute("DELETE FROM imprints;")
    engine.execute("DELETE FROM book_persons;")
    engine.execute("DELETE FROM book_participants;")
    engine.execute("DELETE FROM pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()
