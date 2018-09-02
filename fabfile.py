from config import DockerConfig as def_cfg
from fabric.api import local
from fixtures import insert_fixtures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def __env_safeguard(fab_method):
    """
    This is not a fabric method per se. Useless to call this.
    """
    def check(*args, **kwargs):
        if def_cfg.DEVEL or def_cfg.TESTING:
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
        engine = create_engine(def_cfg.SQLALCHEMY_TEST_DATABASE_URI)
    else:
        engine = create_engine(def_cfg.SQLALCHEMY_DATABASE_URI)
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
def destroy_db_tables(is_test=False):
    """
    Drop all database tables.
    """
    if is_test:
        engine = create_engine(def_cfg.SQLALCHEMY_TEST_DATABASE_URI)
    else:
        engine = create_engine(def_cfg.SQLALCHEMY_DATABASE_URI)
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
    engine = create_engine(def_cfg.SQLALCHEMY_TEST_DATABASE_URI)
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

def __docker_compose_run(entrypoint, service):
    local(__docker_compose_runstr(entrypoint, service))

def __docker_compose_runstr(entrypoint, service):
    return "docker-compose run --entrypoint '%s' %s" % (entrypoint, service)

def load_fixtures():
    __docker_compose_run("python fixtures.py", "web")

def dbdump(dump_name="alexandria.sql"):
    """
    Dump out local database to file.
    """
    # Wow. Such hax. Kids, don't try this at home.
    __docker_compose_run("mysqldump -h db alexandria", "db_runner_1 > alexandria.sql")

def load_db(dump_name="alexandria.sql"):
    # Wow. Such hax. Kids, don't try this at home.
    # Also, this is known to fail sometimes, for reasons unknown (Can't connect
    # to db). So just retry.
    __docker_compose_run("mysql -h db alexandria", "db_runner_1 < %s" % dump_name)

def clone_database():
    """
    Clone the database specified in config.py. Use when working with migrations.

    The new database will be prefixed by the hash of the latest alembic revision.
    """
    dbdump("alexandria_preclone.sql")
    print "For accidents, the back-up `alexandria_preclone.sql` was created."
    from sqlalchemy import Table, MetaData
    from sqlalchemy.sql import select

    engine = create_engine(def_cfg.SQLALCHEMY_DATABASE_URI)
    meta = MetaData(bind=engine)

    last_commit = local("git log --oneline | head -n1 | awk '{print $1}'", capture=True)

    new_db_name = '_'.join((def_cfg.SQL_DB_NAME, last_commit))
    new_test_db_name = '_'.join((new_db_name, "test"))

    __docker_compose_run(
        'mysql -h db -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % new_test_db_name,
        "db"
    )
    __docker_compose_run(
        'mysql -h db -u root -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % new_db_name,
        "db"
    )
    local(
        "%s | %s" %
        (
            __docker_compose_runstr("mysqldump -h db -u root %s" % def_cfg.SQL_DB_NAME, "db_runner_1"),
            __docker_compose_runstr("mysql -h db -u root %s" % new_db_name, "db_runner_2")
        )
    )
    print "NOTE: Must reconfigure this branch to use %s and %s instead" % (new_db_name, new_test_db_name)
    print "Don't forget to reconfigure alembic.ini as well!"

@__env_safeguard
def destroy_database(is_test=False):
    """
    Drop the database. Pass `:is_test=True` to drop the test database instead.
    """
    if is_test:
        __docker_compose_run('mysql -h db -u root -e "DROP DATABASE %s"' % def_cfg.SQL_TEST_DB_NAME, "db_runner_1")
    else:
        __docker_compose_run('mysql -h db -u root -e "DROP DATABASE %s"' % def_cfg.SQL_DB_NAME, "db_runner_1")

def create_database(is_test=False):
    """
    Create the database. Pass `:is_test=True` to create the test database.

    Assumes access to local mysql db via passwordless root.
    """
    if is_test: 
        __docker_compose_run(
            'mysql -h db -u root --protocol=tcp -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % def_cfg.SQL_TEST_DB_NAME,
            "db_runner_1"
        )
    else:
        __docker_compose_run(
            'mysql -h db -u root --protocol=tcp -e "CREATE DATABASE %s DEFAULT CHARACTER SET = utf8"' % def_cfg.SQL_DB_NAME,
            "db_runner_1"
        )
