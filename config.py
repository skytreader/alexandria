import os

"""
DEVEL environment is understood as running a local instance of the app.

TESTING environment on the other hand is understood as running the unit tests
for the app.

SUDO environment should only be triggered for running privileged admin commands,
usually via Invoke.
"""

class DefaultAlexandriaConfig(object):
    APP_NAME = "alexandria"
    DEVEL = True
    TESTING = bool(os.environ.get("_".join((APP_NAME, "TESTING"))))
    SUDO = bool(os.environ.get("_".join((APP_NAME, "SUDO"))))
    
    SQL_HOST = "db"
    SQL_PORT = 3306
    SQL_TEST_PORT = 3309
    SQL_USERNAME = "root"
    SQL_PASSWORD = ""
    SQL_ENGINE = "mysql"
    SQL_DB_NAME = "alexandria"
    SQL_TEST_DB_NAME = "%s_test" % SQL_DB_NAME
    SQLALCHEMY_DATABASE_URI = '%s://%s:%s@%s:%d/%s' % (SQL_ENGINE, SQL_USERNAME,
      SQL_PASSWORD, SQL_HOST, SQL_PORT, SQL_DB_NAME)
    SQLALCHEMY_TEST_DATABASE_URI = '%s://%s:%s@%s_test:%d/%s' % (SQL_ENGINE, SQL_USERNAME,
      SQL_PASSWORD, SQL_HOST, SQL_PORT, SQL_TEST_DB_NAME)
    SQLALCHEMY_ECHO = not DEVEL
    DATABASE_CONNECT_OPTIONS = {"user":"root"}
    
    # Caching, see: https://pythonhosted.org/Flask-Cache/
    # a dictionary containing all the config for Flask-Cache.
    CACHE_CONFIG = {
        "CACHE_TYPE": "redis",
        "CACHE_KEY_PREFIX": "alexandria_",
        "CACHE_REDIS_HOST": "redis"
    }
    
    CACHE_TIMEOUT = 88
    # A little less than 3 years.
    FOREVER_TIMEOUT = 88888888 if not TESTING else 0
    MONTH_TIMEOUT = 2629000
    
    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2
    
    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED     = not TESTING
    WTF_CSRF_ENABLED = CSRF_ENABLED
    
    # Use a secure, unique and absolutely secret key for
    # signing the data. 
    CSRF_SESSION_KEY = "secret"
    
    # Secret key for signing cookies
    SECRET_KEY = "secret"
    
    APP_HOST="0.0.0.0"
    APP_PORT=7070

class TestAlexandriaConfig(DefaultAlexandriaConfig):
    
    SQL_HOST = "db_test"
    SQL_DB_NAME = "alexandria_test"
    #SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s_test
