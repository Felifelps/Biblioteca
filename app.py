from apibiblioteca import app, WATCHER


WATCHER.start()

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
