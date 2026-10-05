from flask import Flask
from flask import render_template, request, redirect, session, url_for
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
import db
import sqlite3
import config
from datetime import datetime

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
    
    username_errors = validate_username(username)
    if username_errors:
        return render_template("register.html", error=password_errors, username=username)
    if password1 != password2:
        return "Virhe: salasanat eivät vastaa."
    password_errors = validate_password(password1)
    if password_errors:
        return render_template("register.html", error=password_errors, username=username)
    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute("users.db", sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "Virhe: tunnus on jo käytossä."
    session["username"] = username
    return render_template(
        "redirect.html",
        title="Tunnus luotu",
        message=f"Tervetuloa, {username}! Sinut ohjataan etusivulle muutaman sekunnin kuluttua."
    )
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

@app.route("/writegame")
def writegame():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"
    return render_template("writegame.html")
@app.route("/submitgame", methods=["POST"])
def submitgame():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"

    #game_id = request.form.get("game_id")
    game_name = request.form["game_name"]
    console = request.form["console"]
    year = request.form["year"]

    if not game_name or not console or not year:
        return "Virhe: kaikki kentät pitää täyttää"
    game_name_errors = validate_game_name(year)
    if game_name_errors:
        return render_template("writegame.html", error=game_name_errors)
    year_errors = validate_year(year)
    if year_errors:
        return render_template("writegame.html", error=year_errors)
    console_errors = validate_console(console)
    if console:
        return render_template("writegame.html", error=console_errors)

    sql = """
        INSERT INTO games (name, console, year) VALUES (?, ?, ?)
        """
    db.execute("games.db", sql, [game_name, console, year])
    username = session["username"]
    return render_template(
        "redirect.html",
        title="Peli lisätty!",
        message=f"Pelinne on nyt lisätty, {username}. Sinut ohjataan etusivulle muutaman sekunnin kuluttua."
    )
@app.route("/submitreview", methods=["POST"])
def submitreview():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"

    review_id = request.form.get("review_id")
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

    if review_id:
        sql = "SELECT username FROM reviews WHERE id = ?"
        owner = db.query("users.db", sql, [review_id])
        if not owner or owner[0]["username"] != session["username"]:
            return "Virhe: et voi muokata toisen käyttäjän arviota"

        sql = """
            UPDATE reviews
            SET game_name = ?, score = ?, review = ?
            WHERE id = ?
        """
        db.execute("users.db", sql, [game_name, score, review_text, review_id])
    else:
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

@app.route("/myreviews")
def myreviews():
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"
    sql = """
    SELECT id, game_name, score, review
    FROM reviews
    WHERE username = ?
    ORDER BY id DESC
    """
    reviews = db.query("users.db", sql, [session["username"]])
    return render_template("myreviews.html", reviews=reviews, username=session["username"])

@app.route("/editreview/<int:review_id>")
def editreview(review_id):
    if not session.get("username"):
        return "Virhe: kirjaudu sisään ensin"

    sql = "SELECT id, username, game_name, score, review FROM reviews WHERE rowid = ?"
    result = db.query("users.db", sql, [review_id])

    if not result:
        return "Virhe: arviota ei löytynyt"

    existing_review = result[0]

    if existing_review["username"] != session["username"]:
        return "Virhe: et voi muokata toisen käyttäjän arviota"

    games = db.query("games.db", "SELECT name FROM games ORDER BY name")
    return render_template("writereview.html", games=games, existing_review=existing_review)

@app.route("/game/<game_name>")
def game(game_name):
    sql = "SELECT id FROM games WHERE name = ?"
    result = db.query("games.db", sql, [game_name])

    if not result:
        return "Virhe: peliä ei loytynyt"

    sql = """
    SELECT username, score, review
    FROM reviews
    WHERE game_name = ?
    ORDER BY id DESC    
    """
    reviews = db.query("users.db", sql, [game_name])
    if reviews:
        average = sum(review["score"] for review in reviews) / len(reviews)
    else:
        average = None

    return render_template("game.html", game_name=game_name, reviews=reviews, average=average)

def validate_password(password):
    errors = []

    if len(password) < 8:
        errors.append("Salasanan pitää olla vähintään 8 merkkiä pitkä.")

    if len(password) > 100:
        errors.append("Salasana voi olla enintään 100 merkkiä pitkä")
    if not any(c.isdigit() for c in password):
        errors.append("Salasanassa pitää olla vähintään yksi numero.")

    if not any(c.isupper() for c in password):
        errors.append("Salasanassa pitää olla vähintään yksi iso kirjain.")

    return errors

def validate_username(username):
    errors = []
    if len(username) == 0:
        errors.append("Käyttäjänimi on tyhjä.")

    if len(username) > 20:
        errors.append("Käyttäjänimi on liian pitkä.")

    return errors

def validate_year(year):
    errors = []

    try:
        year = int(year)
    except ValueError:
        errors.append("Vuosi ei ole numero.")
        return errors
    date_now = datetime.now()
    if not (1958 <= year <= date_now.year):
        errors.append(f"Vuosi pitää olla väliltä 1958-{date_now.year}")
    return errors

def validate_game_name(username):
    errors = []
    if len(username) == 0:
        errors.append("Pelin nimi on tyhjä.")

    if len(username) > 60:
        errors.append("Pelin nimi on liian pitkä.")

    return errors

def validate_console(console):
    errors = []
    if len(console) == 0:
        errors.append("Konsolin nimi on tyhjä.")
    if len(console) > 25:
        errors.append("Konsolin nimi on liian pitkä")
    return errors


def validate_game_name(game_name):
    errors = []
    if len(game_name) == 0:
        errors.append("Pelin nimi on tyhjä.")
    if len(game_name) > 60:
        errors.append("Pelin nimi on liian pitkä")
    return errors
