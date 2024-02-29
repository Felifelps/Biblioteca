# 📚 Biblioteca API

Quart API for the Municipal Library of Milagres - CE

## 📝 Description

This API, developed using [Quart](https://pgjones.gitlab.io/quart/) (an asynchronous web framework for Flask), provides functionalities to interact with the Municipal Library of Milagres - CE. It utilizes the [Render](https://render.com/) platform for hosting and data storage, [Peewee ORM](http://docs.peewee-orm.com/) for database interaction, and includes features such as administrator authentication, manipulation of book data, and export to Excel. The project is managed and packaged with [Poetry](https://python-poetry.org/), a Python dependency management tool.

## 🌐 Website and Hosting

The frontend using this API is available at [Biblioteca Milagres](https://bibliotecamilagres.netlify.app) (Repository: [Biblioteca GitHub](https://github.com/Ditto-157/Biblioteca)). The API is hosted on the [Render](https://render.com/) platform.

## 🛣️ Routes

- `/books/length`: Returns the number of books in the database.
- `/books/page`: Returns a page of books from the database.
- `/books/search`: Searches for books in the database based on the provided parameters.
- `/books/field_values`: Returns the unique values for a given field in the books table.
- `/book/new`: Creates a new book in the database.
- `/book/update`: Updates a book in the database.
- `/book/delete`: Deletes a book from the database.
- `/admin/login`: Authenticates an admin user.
- `/admin/check`: Checks if a given token is valid.
- `/get/data`: Returns the books' data in Excel format.

## 🚀 Technologies Used

- [Quart](https://pgjones.gitlab.io/quart/) (Asynchronous web framework for Flask) 🌐
- [Peewee ORM](http://docs.peewee-orm.com/) (Database Interaction) 🗃️
- [Poetry](https://python-poetry.org/) (Dependency Management) 📦
