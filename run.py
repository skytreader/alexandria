import librarian
from config import APP_HOST, APP_PORT, DEVEL

import time

if __name__ == "__main__":
    for i in range(8):
        try:
            librarian.init_blueprints()
            librarian.init_db()
            librarian.app.run(host=APP_HOST, port=APP_PORT, debug=DEVEL)
        except:
            print "Can't start app, retrying..."
            time.sleep(3)
