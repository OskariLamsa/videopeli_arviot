from flask import Flask
from flask import render_template, request, redirect, session, url_for
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
import db
import sqlite3
import config

app = Flask(__name__)
app.secret_key = config.secret_key
@app.route("/")
def index():
    games = db.query("games.db", "SELECT name from games")
    print(type(games))
    return render_template("index.html", games=games, count=len(games))

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "Virhe: väärä salasana"
    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute("users.db", sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "Virhe: tunnus on jo käytossä."
    return "Tunnus luotu"

@app.route("/login", methods=["post"])
def login():
    username = str(request.form["username"])
    password = request.form["password"]
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query("users.db", sql, [username])[0][0]
    if check_password_hash(password_hash,password):
        session["username"] = username
        return redirect(url_for("index"))
    else:
        return "Virhe: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/loginpage")
def loginpage():
    return render_template("login.html")

@app.route("/writereview")
def writereview():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"

    games = db.query("games.db", "SELECT name FROM games ORDER BY name")
    return render_template("writereview.html", games=games)

@app.route("/submitreview", methods=["POST"])
def submitreview():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"

    game_name = request.form["game_name"]
    score = request.form["score"]
    review_text = request.form["review"]

    if not game_name or not score or not review_text:
        return "Virhe: kaikki kentät pitää täyttää"

    try:
        score = int(score)
    except ValueError:
        return "Virhe: pisteiden pitää olla numero"

    if score < 0 or score > 10:
        return "Virhe: pisteiden pitää olla välillä 0-10"

    sql = "SELECT id FROM games WHERE name = ?"
    result = db.query("games.db", sql, [game_name])

    if not result:
        return "Virhe: peliä ei löytynyt"

    sql = """
        INSERT INTO reviews (username, game_name, score, review)
        VALUES (?, ?, ?, ?)
    """
    db.execute("users.db", sql, [session["username"], game_name, score, review_text])

    return redirect(url_for("index"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/page1")
def page1():
    session["logged_in"] = str(randint(0,10000))
    return "Istunto asetettu"