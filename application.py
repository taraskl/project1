import os, requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#Set the environment variable DATABASE_URL
#app.config['DATABASE_URL'] = "path_to_db"

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

user = []

@app.route("/", methods=["GET", "POST"])
def index():

    user = []
    user_id_int = []
    user_id_name_list = [0]
    username = request.form.get("username")
    password = request.form.get("password")

    # login user    
    if request.method == "POST":
        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", 
            {"username": username, "password": password}).fetchall()
        user_id = db.execute("SELECT id FROM users WHERE username = :username AND password = :password", 
            {"username": username, "password": password}).fetchall()
        user_id_list = user_id[0]
        user_id_int = user_id_list[0]
        session["user_id"] = user_id_int
        return render_template("search.html") 

    # get user name to index page
    if session.get("user_id") is not None:
        user_id_int = session["user_id"]
        user_id_name = db.execute("SELECT username FROM users WHERE id = :id", {"id": user_id_int}).fetchall()
        user_id_name_list = user_id_name[0]


    return render_template("index.html", user=user, user_id=session["user_id"], username=user_id_name_list[0])    

@app.route("/users")
def users():
    users = db.execute("SELECT id, username, password FROM users").fetchall()

    return render_template("users.html", users=users)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
        db.commit()

    return render_template("success.html")  

@app.route("/logout")
def logout():
    session["user_id"] = []

    return render_template("index.html")     

@app.route("/search",methods=["GET", "POST"])
def search():
    books = []
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    year = request.form.get("year")
    if request.method == "POST":
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR title = :title OR author = :author OR year LIKE :year ", 
            {"isbn": isbn, "title": title, "author": author, "year": year}).fetchall()


        return render_template("search.html", books=books)

        # if books == 0:
        #     return render_template("error.html", books=books)

    return render_template("search.html", books=books)    

@app.route("/bookpage/<int:book_id>",methods=["GET", "POST"])
def bookpage(book_id):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()
    user_id = session["user_id"]

    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")

    # Make sure that review nor repeat.
        if db.execute("SELECT book_id, user_id FROM reviews WHERE book_id = :book_id AND user_id = :user_id", 
        {"book_id": book_id, "user_id": user_id}).fetchone():
            return render_template("error.html", message="You already put review to this book!")
        else:    
            db.execute("INSERT INTO reviews (rating, review, user_id, book_id) VALUES (:rating, :review, :user_id, :book_id)",
                {"rating": rating, "review": review, "user_id": user_id, "book_id": book_id})
            db.commit()

            return render_template("success.html")

    # Take api from www.goodreads.com
    isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book_id}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", 
        params={"key": "ubpONM2BPSrMnFHwGMn00w", "isbns": isbn})        
    data = res.json()
    data_books = data["books"]
    data_books_list = data_books[0]


    return render_template("bookpage.html", book=book, reviews=reviews, data=data_books_list, isbn=isbn)            

@app.route("/api/books/<int:book_id>")
def book_api(book_id):
    """Return details about a single flight."""

    # Make sure flight exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid book_id"}), 422

    # Get all passengers.
    # passengers = flight.passengers
    # names = []
    # for passenger in passengers:
    #     names.append(passenger.name)
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": 28,
            "average_score": 5.0
        })

# postgres://jfejmfpcxdqlsi:73652fbc86ab0ce7ea97867d038807c510c792b7de8221d20859f1f64b656aaa@ec2-54-217-216-149.eu-west-1.compute.amazonaws.com:5432/dftg51cd4b1p9