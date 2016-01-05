from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TEST_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fixtures import insert_fixtures

def reset_db_data():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("TRUNCATE TABLE IF EXISTS alembic_version;")
    engine.execute("TRUNCATE TABLE IF EXISTS librarians;")
    engine.execute("TRUNCATE TABLE IF EXISTS roles;")
    engine.execute("TRUNCATE TABLE IF EXISTS genres;")
    engine.execute("TRUNCATE TABLE IF EXISTS books;")
    engine.execute("TRUNCATE TABLE IF EXISTS book_companies;")
    engine.execute("TRUNCATE TABLE IF EXISTS imprints;")
    engine.execute("TRUNCATE TABLE IF EXISTS book_persons;")
    engine.execute("TRUNCATE TABLE IF EXISTS book_participants;")
    engine.execute("TRUNCATE TABLE IF EXISTS printers;")
    engine.execute("TRUNCATE TABLE IF EXISTS pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

    insert_fixtures(engine, session)

def destroy_db_tables():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("DROP TABLE IF EXISTS alembic_version;")
    engine.execute("DROP TABLE IF EXISTS librarians;")
    engine.execute("DROP TABLE IF EXISTS roles;")
    engine.execute("DROP TABLE IF EXISTS genres;")
    engine.execute("DROP TABLE IF EXISTS books;")
    engine.execute("DROP TABLE IF EXISTS book_companies;")
    engine.execute("DROP TABLE IF EXISTS imprints;")
    engine.execute("DROP TABLE IF EXISTS book_persons;")
    engine.execute("DROP TABLE IF EXISTS book_participants;")
    engine.execute("DROP TABLE IF EXISTS printers;")
    engine.execute("DROP TABLE IF EXISTS pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

def manual_test_cleanup():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("DELETE FROM alembic_version;")
    engine.execute("DELETE FROM librarians;")
    engine.execute("DELETE FROM roles;")
    engine.execute("DELETE FROM genres;")
    engine.execute("DELETE FROM books;")
    engine.execute("DELETE FROM book_companies;")
    engine.execute("DELETE FROM imprints;")
    engine.execute("DELETE FROM book_persons;")
    engine.execute("DELETE FROM book_participants;")
    engine.execute("DELETE FROM printers;")
    engine.execute("DELETE FROM pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()
