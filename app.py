from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging


app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


# Our list of books
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "1984", "author": "George Orwell"}
]


def validate_book_data(data):
    if "title" not in data or "author" not in data:
        return False
    return True


@app.route('/api/books', methods=['GET', 'POST'])
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def handle_books():
    if request.method == 'POST':
        # Get the new book data from the client
        new_book = request.get_json()

        if not validate_book_data(new_book):
            return jsonify({"error": "Invalid book data"}), 400
        
        # Generate a new ID for the book
        new_id = max(book['id'] for book in books) + 1
        new_book['id'] = new_id
        
        # Add the new book to our list
        books.append(new_book)
        
        # Return the new book data to the client
        return jsonify(new_book), 201
    else:
        # Handle the GET request with pagination
        page = int(request.args.get('page', 1))  # Default page is 1 if not specified
        limit = int(request.args.get('limit', 10))  # Default limit is 10 if not specified

        # Calculate start and end indices for pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit

        # Slice the list of books to get only the paginated books
        paginated_books = books[start_index:end_index]

        # Return the paginated books as JSON
        return jsonify(paginated_books)


def find_book_by_id(book_id):
    """Find the book with the id `book_id`.
    If there is no book with this id, return None."""
    # Iterate over the books list to find a book with the given id
    for book in books:
        if book["id"] == book_id:
            return book
    return None  # Return None if the book isn't found

@app.route('/api/books/<int:id>', methods=['PUT'])
def handle_book(id):
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        return '', 404

    # Update the book with the new data from the request body
    new_data = request.get_json()
    book.update(new_data)

    # Return the updated book data
    return jsonify(book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        return '', 404

    # Remove the book from the list
    # TODO: implement this
    ...

    # Return the deleted book
    return jsonify(book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    # Find the book with the given ID
    book = find_book_by_id(id)

    # If the book wasn't found, return a 404 error
    if book is None:
        return '', 404

    # Remove the book from the list by filtering it out
    global books
    books = [b for b in books if b['id'] != id]

    # Return the deleted book as confirmation
    return jsonify(book), 200


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)