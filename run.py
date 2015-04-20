from app import app
from config import APP_HOST, APP_PORT, DEBUG

if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG)
