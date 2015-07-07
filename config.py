# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1/alexandria'
SQLALCHEMY_TEST_DATABASE_URI = 'mysql://root@127.0.0.1/alexandria_test'
SQLALCHEMY_ECHO = DEBUG
DATABASE_CONNECT_OPTIONS = {"user":"root"}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = not DEBUG

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

APP_HOST="0.0.0.0"
APP_PORT=8080
