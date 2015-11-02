from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("DROP TABLE librarians;")
    engine.execute("DROP TABLE roles;")
    engine.execute("DROP TABLE genres;")
    engine.execute("DROP TABLE books;")
    engine.execute("DROP TABLE book_companies;")
    engine.execute("DROP TABLE imprints;")
    engine.execute("DROP TABLE book_persons;")
    engine.execute("DROP TABLE book_participants;")
    engine.execute("DROP TABLE printers;")
    engine.execute("DROP TABLE pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()
