import librarian
from config import APP_HOST, APP_PORT, DEVEL

import time
import traceback

if __name__ == "__main__":
    exp_backoff = 0
    while True:
        try:
            librarian.init_blueprints()
            librarian.init_db()
            librarian.app.run(host=APP_HOST, port=APP_PORT, debug=DEVEL)
        except (KeyboardInterrupt, SystemExit):
            print "KeyboardInterrupt or SystemExit"
            raise
        except Exception:
            traceback.print_exc()
            print "Can't start app, retrying..."
            exp_backoff += 1
            time.sleep(3 ** exp_backoff)
