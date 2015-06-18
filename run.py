import librarian
from config import APP_HOST, APP_PORT, DEBUG

if __name__ == "__main__":
    librarian.init_db()
    librarian.app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG)
