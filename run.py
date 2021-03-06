from __future__ import print_function
import librarian
from config import DefaultAlexandriaConfig as cfg

import os
import socket
import time
import traceback


if __name__ == "__main__":
    exp_backoff = 0
    print("Welcome to Alexandria. Starting up...")
    while True:
        try:
            librarian.init_blueprints()
            librarian.init_db()
            librarian.app.run(host=cfg.APP_HOST, port=cfg.APP_PORT, debug=cfg.DEVEL)
        # We need to catch socket.error too since it seems that Werkzeug (used
        # Flask's _development_ environment) uses socket.py and somewhere there
        # they already catch KeyboardInterrupt. Not doing this leads to a
        # situation where you need to CTRL + C twice in order to quit the
        # development server.
        except (KeyboardInterrupt, SystemExit, socket.error):
            raise
        except Exception as e:
            traceback.print_exc()
            print("Can't start app, retrying...")
            exp_backoff += 1
            time.sleep(3 ** exp_backoff)
