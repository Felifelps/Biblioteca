from apibiblioteca import app, AUTO_REQUESTING, UPLOADER

#AUTO_REQUESTING.start()

#UPLOADER.start()

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)