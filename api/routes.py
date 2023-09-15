from flask import Flask, request
from flask import render_template
from flask_cors import CORS
from api.data_handler import DataHandler

app = Flask('Biblioteca')

cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

#Search books page
@app.route('/search/')
def search():
    return '<h1>Search page</h1>'

#Add books
@app.route('/book/add/')
def add_book():
    return '<h1>Add books</h1>'

#Edit books
@app.route('/book/<int:id>/edit/')
def edit_book(id):
    return '<h1>Edit books</h1>'

#Delete books
@app.route('/book/<int:id>/delete/')
def delete_book(id):
    return '<h1>Delete books</h1>'

#Get book information
@app.route('/book/<int:id>/')
def get_book(id):
    return '<h1>Look at a book</h1>'

#Add shelfs
@app.route('/shelf/add//')
def add_shelf():
    return '<h1>Add shelfs</h1>'

#Edit shelfs
@app.route('/shelf/<int:id>/edit/')
def edit_shelf(id):
    return '<h1>Edit shelfs</h1>'

#Delete shelfs
@app.route('/shelf/<int:id>/delete/')
def delete_shelf(id):
    return '<h1>Delete shelfs</h1>'

#Add bookcases
@app.route('/bookcase/add//')
def add_bookcase():
    return '<h1>Add bookcases</h1>'

#Edit bookcases
@app.route('/bookcase/<int:id>/edit/')
def edit_bookcase(id):
    return '<h1>Edit bookcases</h1>'

#Delete bookcases
@app.route('/bookcase/<int:id>/delete/')
def delete_bookcase(id):
    return '<h1>Delete bookcases</h1>'

#Main page
@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == 'POST':
        new_file = open('teste.file', 'wb')
        for i in request.files['file']:
            new_file.write(i)
        DataHandler().upload_file(name)
    return render_template('index.html')
