from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fixtures import insert_fixtures

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("TRUNCATE TABLE librarians;")
    engine.execute("TRUNCATE TABLE roles;")
    engine.execute("TRUNCATE TABLE genres;")
    engine.execute("TRUNCATE TABLE books;")
    engine.execute("TRUNCATE TABLE book_companies;")
    engine.execute("TRUNCATE TABLE imprints;")
    engine.execute("TRUNCATE TABLE book_persons;")
    engine.execute("TRUNCATE TABLE book_participants;")
    engine.execute("TRUNCATE TABLE pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

    insert_fixtures(engine, session)
