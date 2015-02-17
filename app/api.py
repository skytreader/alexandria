from flask import Blueprint

librarian_api = Blueprint("librarian_api", __name__)

@librarian_api.route("/book_adder")
def book_adder():
    return "Hello there."
