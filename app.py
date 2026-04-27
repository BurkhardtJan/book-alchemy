from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '12345SecretKey67890'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


def setup_create():
    """Create the table. Only used to initialize the database."""
    with app.app_context():
        db.create_all()


@app.route('/', methods=['GET'])
def home():
    """Shows home page. Manages sort und different filters with AND logic."""
    search_book_title = request.args.get('search_book_title')
    search_book_author = request.args.get('search_book_author')
    search_book_year = request.args.get('search_book_year')
    sort_by = request.args.get('sort', 'title')
    direction = request.args.get('direction', 'asc')

    query = Book.query
    if search_book_author:
        query = query.join(Author).filter(Author.name.like(f"%{search_book_author}%"))
    if search_book_title:
        query = query.filter(Book.title.like(f"%{search_book_title}%"))
    if search_book_year:
        query = query.filter(Book.publication_year.like(f"%{search_book_year}%"))

    if sort_by == 'author':
        sort_column = Author.name
        query = query.join(Author)
    elif sort_by == 'year':
        sort_column = Book.publication_year
    else:
        sort_column = Book.title

    if direction == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    books = query.all()
    authors = Author.query.all()
    return render_template("home.html", books=books, authors=authors), 200


@app.route('/add_author', methods=['GET'])
def add_author_webpage():
    """Shows page to add author"""
    return render_template("add_author.html"), 200


@app.route('/add_author', methods=['POST'])
def add_author():
    """Adds author to database"""
    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    date_of_death = request.form.get("date_of_death")

    birth_date = None
    if birthdate:
        birth_date = datetime.strptime(birthdate, '%Y-%m-%d').date()

    death_date = None
    if date_of_death:
        death_date = datetime.strptime(date_of_death, '%Y-%m-%d').date()

    new_author = Author(
        name=name,
        birth_date=birth_date,
        death_date=death_date
    )
    db.session.add(new_author)
    db.session.commit()
    success_message = "Author successfully added!"
    return render_template("add_author.html", success_message=success_message), 201


@app.route('/add_book', methods=['GET'])
def add_book_webpage():
    """Shows page to add book"""
    authors = Author.query.all()
    return render_template("add_book.html", authors=authors), 200


@app.route('/add_book', methods=['POST'])
def add_book():
    """Adds book to database"""
    title = request.form.get("title")
    isbn = request.form.get("isbn")
    author_id = request.form.get("author_id")
    publication_year = request.form.get("publication_year")

    new_book = Book(
        isbn=isbn,
        title=title,
        publication_year=publication_year,
        author_id=author_id
    )
    db.session.add(new_book)
    db.session.commit()
    success_message = "Book successfully added!"
    authors = Author.query.all()
    return render_template("add_book.html", success_message=success_message, authors=authors), 201


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a Book by ID"""
    book = Book.query.get_or_404(book_id)
    author = book.author
    db.session.delete(book)
    title = book.title
    flash(f"Removed Book '{title}'")
    if not author.books:
        name = author.name
        db.session.delete(author)
        flash(f"Removed Author '{name}'")
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """Delete a Book by ID"""
    author = Author.query.get_or_404(author_id)
    name = author.name
    for book in author.books:
        title = book.title
        db.session.delete(book)
        flash(f"Removed Book '{title}'")
    db.session.delete(author)
    db.session.commit()
    flash(f"Removed Author '{name}' with all books")
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>', methods=['GET'])
def show_book(book_id):
    """Shows detail page of book by ID"""
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book), 200


@app.route('/author/<int:author_id>', methods=['GET'])
def show_author(author_id):
    """Shows detail page of author by ID"""
    author = Author.query.get_or_404(author_id)
    return render_template("author_detail.html", author=author), 200


if __name__ == '__main__':
    setup_create()
    app.run(host="0.0.0.0", port=5002, debug=True)
