"""
This module provides the implementation of the biblioteca API.

The biblioteca API is a simple library management system that allows users
to search for books, check out books, and return books. It also allows
administrators to add new books to the library and remove books from the
library.

The following classes are provided in this module:

* `Book`: A class that represents a book in the library.
* `User`: A class that represents a user of the library.
* `Library`: A class that represents the library itself and manages the
collection of books and the list of users.
"""

from .routes import app
from .watcher import WATCHER
from .models import *
