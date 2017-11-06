import librarian
from config import APP_HOST, APP_PORT, DEVEL

import socket
import time
import traceback

if __name__ == "__main__":
    exp_backoff = 0
    while True:
        try:
            librarian.init_blueprints()
            librarian.init_db()
            librarian.app.run(host=APP_HOST, port=APP_PORT, debug=DEVEL)
        # We need to catch socket.error too since it seems that Werkzeug (used
        # Flask's _development_ environment) uses socket.py and somewhere there
        # they already catch KeyboardInterrupt. Not doing this leads to a
        # situation where you need to CTRL + C twice in order to quit the
        # development server.
        except (KeyboardInterrupt, SystemExit, socket.error):
            raise
        except Exception as e:
            traceback.print_exc()
            print "Can't start app, retrying..."
            exp_backoff += 1
            time.sleep(3 ** exp_backoff)
