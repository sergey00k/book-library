from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    birth_date = db.Column(db.String)
    date_of_death = db.Column(db.String)

class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), autoincrement=True)
    cover_url = db.Column(db.String)

    author = db.relationship('Author', backref=db.backref('books', lazy=True))

def get_all_books():
    books = {}
    books_table = db.session.query(Book).all()
    for row in books_table:
        author_row = db.session.query(Author).filter(Author.author_id == row.author_id).one()
        author_name = author_row.name
        books[row.book_id] = {'image_url': row.cover_url, 'title': row.title, 'author': author_name, 'publication_year': row.publication_year}
    return books
    

def get_all_authors():
    authors = []
    authors_table = db.session.query(Author).all()
    for row in authors_table:
        author = {row.author_id: row.name}
        authors.append(author)
    return authors

def delete_book(book_id):
    row_to_delete = db.session.query(Book).get(book_id)
    db.session.delete(row_to_delete)
    db.session.commit()

with app.app_context():
   db.create_all()