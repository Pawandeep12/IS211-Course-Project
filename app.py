import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    page_count = db.Column(db.Integer)
    average_rating = db.Column(db.Float)
    thumbnail_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        data = response.json()
        
        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            title = book_info.get('title', 'No title available')
            author = ', '.join(book_info.get('authors', ['Unknown']))
            page_count = book_info.get('pageCount', 'N/A')
            average_rating = book_info.get('averageRating', 'N/A')
            thumbnail = book_info.get('imageLinks', {}).get('thumbnail', '')
            
            return render_template('add_book.html', title=title, author=author, 
                                   page_count=page_count, average_rating=average_rating, 
                                   thumbnail=thumbnail)
        else:
            flash("No results found for this ISBN.", 'error')
    return render_template('search_book.html')


@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    page_count = request.form['page_count']
    average_rating = request.form['average_rating']
    thumbnail_url = request.form['thumbnail_url']
    user_id = 1  
    
    new_book = Book(title=title, author=author, page_count=page_count, 
                    average_rating=average_rating, thumbnail_url=thumbnail_url, 
                    user_id=user_id)
    db.session.add(new_book)
    db.session.commit()
    
    flash("Book added successfully!", 'success')
    return redirect(url_for('view_books'))


@app.route('/books')
def view_books():
    user_id = 1  
    books = Book.query.filter_by(user_id=user_id).all()
    return render_template('view_books.html', books=books)


@app.route('/delete_book/<int:book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", 'success')
    return redirect(url_for('view_books'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
