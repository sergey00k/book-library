from flask import Flask, request, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
import data_models
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Set to True or False as per your needs

db = SQLAlchemy()
db.init_app(app)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'GET':
        return render_template('add_author.html')
    else:
        name = request.form['name']
        birth_date = request.form['birth_date']
        if len(request.form['death_date']) != 0:
            death_date = request.form['death_date']
        else:
            death_date = "N/A"
        try:
            new_author = data_models.Author(name=name, birth_date=birth_date, date_of_death=death_date)

            db.session.add(new_author)
            db.session.commit()
        except Exception as e:
            return render_template('error.html',header=e, error=e)
        return render_template('success.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        authors = data_models.get_all_authors()
        return render_template('add_book.html', authors=authors)
    else:
        title = request.form['title']
        publication_year = request.form['publication_year']
        isbn = request.form['isbn']
        author = request.form['author']
        payload = {'key': 'AIzaSyAk1EL9cT7hi2OHlHiZSRpUDovkO3G5950', 'q': 'isbn:' + isbn}
        response = requests.get('https://www.googleapis.com/books/v1/volumes', params=payload)
        print(response)
        if response.status_code != 200:
            return render_template('error.html', header='External api not responding', error='Sorry, the api for fetching movie information is not available,\n please try again later.')
        else:
            content = response.json()
        if 'Error' in content:
            return render_template('error.html', header='book not found', error='Sorry, the book you were looking for could not be found.')
        else:
            with current_app.app_context():
                author_instance = data_models.Author.query.get(int(author))
            new_book = data_models.Book(title=title, publication_year=publication_year, isbn=isbn, author=author_instance, cover_url=str(content['items'][0]['volumeInfo']['imageLinks']['thumbnail']))

            db.session.add(new_book)

            db.session.commit()
            return render_template('success.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        books = data_models.get_all_books()
        return render_template('home.html', books=books)
    else:
        search = request.form['search']
        search_results = 0
        books = data_models.get_all_books()
        matched_books = {}
        for book_id, book in books.items():
            if search.lower() == book['title'].lower()[:len(search)]:
                matched_books[book_id] = book
                search_results += 1
        if search_results == 0:
            return render_template('error.html', header='No Matches', error='Sorry, there are no books that match your search criteria.')
        else:
            books = data_models.get_all_books()
            return render_template('home.html', books=matched_books)

@app.route('/home/delete_book/<book_id>')
def delete_book(book_id):
    try:
        data_models.delete_book(book_id)
    except Exception as e:
        return render_template('error.html', error=e)
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug=True)