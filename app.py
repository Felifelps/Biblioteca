from apibiblioteca import app, watcher

watcher.start()

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')