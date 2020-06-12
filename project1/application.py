import os

from flask import Flask, session, render_template, url_for, request, redirect, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Helper functions
def get_reviews(book_id):
    reviews = db.execute(
        'SELECT  username, review_score, review_text, time, book_id FROM users JOIN reviews \
        ON reviews.user_id = users.id WHERE book_id=:book_id',
        {"book_id":book_id}
    )
    
    return reviews


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT username FROM users WHERE username = :username', {"username":username}
            ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO users (username, password) VALUES (:username, :password)', 
                {"username":username, "password":generate_password_hash(password)}
            )
            db.commit()
            return redirect(url_for('login'))
        
        flash(error)

    return render_template('register.html')

@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE username = :username', {"username":username}
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))

        flash(error)
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/search", methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        query = request.form['query']
        
        query = query.title()
        query = "%" + query + "%"
        
        results = db.execute(
            "SELECT * FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query",
            {"query":query}
        ).fetchall()
    
    if results is None:
        flash("No books match that description.")
        
    return render_template('search.html', results=results)
    
@app.route("/book/<isbn>", methods=('GET', 'POST'))
def book_reviews(isbn):
    book = db.execute(
        'SELECT * FROM books WHERE isbn = :isbn',
        {"isbn":isbn}
    ).fetchone()
    
    book_id = book[0]
    
    reviews = get_reviews(book_id)
    
    # Code for writing a new review
    if request.method == 'POST':
        if session.get('username') is None:
            flash("Must be logged in to write a review.")
        else:
            already_reviewed = db.execute(
                'SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id',
                {"user_id":session['user_id'], "book_id":book_id}
            ).fetchone()
            
            if already_reviewed is not None:
                flash("Can only review a book one time.")
            else:
                review_score = request.form['review_score']
                review_text = request.form['review_text']
                
                db.execute(
                    'INSERT INTO reviews (user_id, book_id, review_score, review_text) \
                    VALUES(:user_id, :book_id, :review_score, :review_text)',
                    {"user_id":session['user_id'], "book_id":book_id, "review_score":int(review_score), "review_text":review_text}
                )
                db.commit()
                
                return redirect('/book/' + isbn)
            
    
    
    return render_template('book.html', book=book, reviews=reviews)
    
