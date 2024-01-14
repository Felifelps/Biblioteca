"""This module contains the main entry point for the
biblioteca API.

The module imports the `app` and `WATCHER` objects from
the `apibiblioteca` module.

The `WATCHER.start()` function is called to start the
watcher thread.

"""

from apibiblioteca import app, WATCHER

WATCHER.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
