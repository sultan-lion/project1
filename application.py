import os
from flask import Flask, session, render_template,jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    surname = request.form.get("surname")
    email = request.form.get("email")
    name = request.form.get("username")
    password= request.form.get("password")
    if not name or not surname or not email or not username or not password:
        return render_template("error.html", message="Please fill the regstration form completely")

    if db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("error.html", message="You are already registered")

    db.execute("INSERT INTO accounts (name, surname, email, username, password) VALUES (:name, :surname, :email, :username, :password)",
            {"name": name, "surname": surname, "email": email, "username": username, "password": password })
    db.commit()

    return render_template("success.html",message="You have successfully been registered on the website!")

@app.route("/search", methods=["POST"])
def login():
    username = request.form.get("username2")
    password = request.form.get("password2")

    if not username or not password:
        return render_template("error.html", message="Please type both the username and the password")

    # Make sure flight exists.
    if db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).rowcount == 0:
        return render_template("error.html", message="Username does not exist")

    if db.execute("SELECT * FROM accounts WHERE username = :username AND password= :password", {"username": username ,"password": password}).rowcount == 0:
         return render_template("error.html", message="Wrong Password")
    session["user"] = db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username ,"password": password}).fetchone()
    return render_template("search.html")

@app.route("/search/books", methods=["POST"])
def search():
    book_isbn = request.form.get("book_isbn")
    book_isbn = "%"+ book_isbn + "%"
    search_results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": book_isbn}).fetchall()
    return render_template("results.html", search_results = search_results)

@app.route("/search/books/<book_isbn>")
def review(book_isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    book_rev = db.execute("SELECT book_isbn,rev_text, rev_rate,username FROM review JOIN accounts on review.user_id = accounts.id WHERE book_isbn = :book_isbn", {"book_isbn": book_isbn}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "y2a7MXJzKHF9HGrshbUsAQ", "isbns": book_isbn})
    grv = res.json()
    grv = {'avg_rate': grv["books"][0]["average_rating"], 'rate_count': grv["books"][0]["ratings_count"]}

    return render_template("book.html",book=book,book_rev=book_rev,grv=grv)


@app.route("/search/books/<book_isbn>/submitreview",methods=["POST"])
def submit(book_isbn):
    rev_text = request.form.get("text")
    try:
        rev_rate = int(request.form.get("rate"))
    except ValueError:
        return render_template("error.html", message="Please rate the Book!")
    #Check if you have previously submitted a review for this book
    if db.execute("SELECT * FROM review WHERE book_isbn = :book_isbn AND user_id= :user_id", {"book_isbn": book_isbn, "user_id": session["user"].id}).rowcount != 0:
        return render_template("error.html", message="You have already submitted a review for this book!")

     #INSERT INTO DATABASE'S REVIEW TABLE
    if rev_text:
        db.execute("INSERT INTO review (rev_text, rev_rate, book_isbn, user_id) VALUES (:rev_text, :rev_rate, :book_isbn, :user_id)",
            {"rev_text": rev_text, "rev_rate": rev_rate, "book_isbn": book_isbn, "user_id": session["user"].id })
        db.commit()
    else:
        db.execute("INSERT INTO review (rev_rate, book_isbn, user_id) VALUES (:rev_rate, :book_isbn, :user_id)",
            {"rev_rate": rev_rate, "book_isbn": book_isbn, "user_id": session["user"].id })
        db.commit()

    #update rev count
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book.rev_count is None:
        new_rev_count=1
    else:
        new_rev_count = book.rev_count + 1
    db.execute("UPDATE books SET rev_count = :new_count WHERE isbn = :isbn",{"isbn": book_isbn, "new_count": new_rev_count})
    db.commit()

   #update average score
    if db.execute("SELECT * FROM review WHERE book_isbn = :book_isbn",{"book_isbn": book_isbn}).rowcount == 1:
        avg = float(rev_rate)
        db.execute("UPDATE books SET avg_score = :avg WHERE isbn = :isbn",{"isbn": book_isbn, "avg": avg})
        db.commit()
        return render_template("success.html",message="You have successfully submitted your review!")
    else:
        oldrates = db.execute("SELECT * FROM review WHERE book_isbn = :book_isbn",{"book_isbn": book_isbn}).fetchall()
        sum=0
        for rev in oldrates:
            sum = sum + int(rev.rev_rate)
        avg = sum/new_rev_count
        db.execute("UPDATE books SET avg_score = :avg WHERE isbn = :isbn",{"isbn": book_isbn, "avg": avg})
        db.commit()
        return render_template("success.html",message="You have successfully submitted your review!")


# API ROUTES
@app.route("/api/<isbn>")
def book_api(isbn):
    if db.execute("SELECT * FROM books WHERE isbn = :book_isbn",{"book_isbn": isbn}).rowcount == 0:
        return jsonify({"error": "Invalid ISBN or not in the Database"}), 404
    else:
        book = db.execute("SELECT * FROM books WHERE isbn = :book_isbn",{"book_isbn": isbn}).fetchone()
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": book.rev_count,
            "average_score": book.avg_score
        })
