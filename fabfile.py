from config import (
  DEVEL, SQL_DB_NAME, SQL_TEST_DB_NAME, SQLALCHEMY_DATABASE_URI,
  SQLALCHEMY_TEST_DATABASE_URI, TESTING
)
from fabric.api import local
from fixtures import insert_fixtures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def __env_safeguard(fab_method):
    """
    This is not a fabric method per se. Useless to call this.
    """
    def check(*args, **kwargs):
        if DEVEL or TESTING:
            fab_method(*args, **kwargs)
        else:
            print "Prevented by env_safeguard"

    return check

@__env_safeguard
def reset_db_data(is_test=False):
    """
    Truncate all database tables. Pass `is_test:True` to reset test db.
    """
    if is_test:
        engine = create_engine(SQLALCHEMY_TEST_DATABASE_URI)
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)()
    engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
    engine.execute("TRUNCATE alembic_version;")
    engine.execute("TRUNCATE librarians;")
    engine.execute("TRUNCATE roles;")
    engine.execute("TRUNCATE genres;")
    engine.execute("TRUNCATE books;")
    engine.execute("TRUNCATE book_companies;")
    engine.execute("TRUNCATE imprints;")
    engine.execute("TRUNCATE contributors;")
    engine.execute("TRUNCATE book_contributions;")
    engine.execute("TRUNCATE printers;")
    engine.execute("TRUNCATE pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

    insert_fixtures(engine, session)

@__env_safeguard
def destroy_db_tables():
    """
    Drop all database tables.
    """
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
    engine.execute("DROP TABLE IF EXISTS contributors;")
    engine.execute("DROP TABLE IF EXISTS book_contributions;")
    engine.execute("DROP TABLE IF EXISTS printers;")
    engine.execute("DROP TABLE IF EXISTS pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

def manual_test_cleanup():
    """
    Delete all tables in test database.
    """
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
    engine.execute("DELETE FROM contributors;")
    engine.execute("DELETE FROM book_contributions;")
    engine.execute("DELETE FROM printers;")
    engine.execute("DELETE FROM pseudonyms;")
    engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

def dbdump(dump_name="alexandria.sql"):
    """
    Dump out local database to file. Assumes access to local mysql db via
    passwordless root.
    """
    local("mysqldump -u root alexandria > %s" % dump_name)

def clone_database():
    """
    Clone the database specified in config.py. Use when working with migrations.

    The new database will be prefixed by the hash of the latest alembic revision.
    """
    dbdump("alexandria_preclone.sql")
    print "For accidents, the back-up `alexandria_preclone.sql` was created."
    from sqlalchemy import Table, MetaData
    from sqlalchemy.sql import select

    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    meta = MetaData(bind=engine)

    alembic_version_table = Table("alembic_version", meta, autoload=True)
    alembic_version = engine.execute(select([alembic_version_table])
      .select_from(alembic_version_table)).first()[0]

    new_db_name = '_'.join((SQL_DB_NAME, alembic_version))
    new_test_db_name = '_'.join((new_db_name, "test"))

    local('mysql -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % new_test_db_name)
    local('mysql -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % new_db_name)
    local("mysqldump -u root %s | mysql -u root %s" % (SQL_DB_NAME, new_db_name))
    print "NOTE: Must reconfigure this branch to use %s and %s instead" % (new_db_name, new_test_db_name)
    print "Don't forget to reconfigure alembic.ini as well!"

@__env_safeguard
def destroy_database(is_test=False):
    """
    Drop the database. Pass `:is_test=True` to drop the test database instead.

    Assumes access to local mysql db via passwordless root.
    """
    if is_test:
        local('mysql -u root -e "DROP DATABASE %s"' % SQL_TEST_DB_NAME)
    else:
        local('mysql -u root -e "DROP DATABASE %s"' % SQL_DB_NAME)

def create_database(is_test=False):
    """
    Create the database. Pass `:is_test=True` to create the test database.

    Assumes access to local mysql db via passwordless root.
    """
    if is_test: 
        local('mysql -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % SQL_TEST_DB_NAME)
    else:
        local('mysql -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % SQL_DB_NAME)
