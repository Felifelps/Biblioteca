from apibiblioteca import app, WATCHER

WATCHER.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
