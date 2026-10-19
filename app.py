from flask import Flask
from flask import render_template, request, redirect, session, url_for, abort
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
import db
import sqlite3
import config
import input_validator
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMSITE="Lax",
)
@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return {"csrf_token": session["csrf_token"]}

@app.before_request
def csrf_protect():
    if request.method == "POST":
        sent = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not secrets.compare_digest(sent, expected):
            abort(403)
@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    console = request.args.get("console", "").strip()

    conditions = []
    params = []

    if query:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        conditions.append("name LIKE ? ESCAPE '\\'")
        params.append("%" + escaped + "%")

    if console:
        conditions.append("console = ?")
        params.append(console)

    sql = "SELECT name, console FROM games"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY name"

    games = db.query("games.db", sql, params)
    consoles = db.query("games.db", "SELECT DISTINCT console FROM games ORDER BY console")

    return render_template(
        "index.html",
        games=games,
        count=len(games),
        query=query,
        console=console,
        consoles=consoles,
    )
@app.route("/create", methods=["POST"])
def create():
    username = request.form.get("username", "")
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")

    username_errors = input_validator.validate_username(username)
    password_errors = input_validator.validate_password(password1, password2)

    if username_errors or password_errors:
        return render_template("register.html", error=username_errors + password_errors)

    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute("users.db", sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("register.html", error=["Virhe: tunnus on jo käytössä."])

    session["username"] = username
    return render_template(
        "redirect.html",
        title="Tunnus luotu",
        message=f"Tervetuloa, {username}! Sinut ohjataan etusivulle muutaman sekunnin kuluttua."
    )

@app.route("/login", methods=["post"])
def login():
    username = str(request.form.get("username", ""))
    password = request.form.get("password", "")
    sql = "SELECT password_hash FROM users WHERE username = ?"
    try:
        password_hash = db.query("users.db", sql, [username])[0][0]
    except IndexError:
        return "Virhe: väärä tunnus tai salasana"
    if check_password_hash(password_hash,password):
        session["username"] = username
        return redirect(url_for("index"))
    else:
        return "Virhe: väärä tunnus tai salasana"

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/loginpage")
def loginpage():
    return render_template("login.html")

@app.route("/writereview")
def writereview():
    reguire_login()

    games = db.query("games.db", "SELECT name FROM games ORDER BY name")
    return render_template("writereview.html", games=games)

@app.route("/writegame")
def writegame():
    reguire_login()
    return render_template("writegame.html", consoles=config.CONSOLES)

@app.route("/submitgame", methods=["POST"])
def submitgame():
    reguire_login()

    game_name = request.form.get("game_name", "")
    console = request.form.get("console", "")
    year = request.form.get("year", "")

    if not game_name or not console or not year:
        return "Virhe: kaikki kentät pitää täyttää"

    if db.check_if_game_exists("games.db", game_name):
        return render_template("writegame.html", error="Virhe: Peli löytyy jo sivustolta!")
        
    game_name_errors = input_validator.validate_game_name(game_name)
    year_errors = input_validator.validate_year(year)
    console_errors = input_validator.validate_console(console)
    
    if game_name_errors or year_errors or console_errors:
        return render_template("writegame.html", error=game_name_errors + year_errors + console_errors)
    
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
    reguire_login()

    review_id = request.form.get("review_id", "")
    game_name = request.form.get("game_name", "")
    score = request.form.get("score", "")
    review_text = request.form.get("review", "")
    if not game_name or not score or not review_text:
        return "Virhe: kaikki kentät pitää täyttää"

    if input_validator.validate_review_score(score) != None:
        return input_validator.validate_review_score(score)

    sql = "SELECT id FROM games WHERE name = ?"
    result = db.query("games.db", sql, [game_name])

    if not result:
        return "Virhe: peliä ei löytynyt"

    if review_id:
        # Arvion editointi
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
        # Uusi arvio
        sql = """
            INSERT INTO reviews (username, game_name, score, review, thumbs_up, thumbs_down)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute("users.db", sql, [session["username"], game_name, score, review_text, 0, 0])

    return redirect(url_for("index"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/myreviews")
def myreviews():
    reguire_login()
    sql = """
    SELECT id, game_name, score, review
    FROM reviews
    WHERE username = ?
    ORDER BY id DESC
    """
    reviews = db.query("users.db", sql, [session["username"]])
    average = round(sum(r["score"] for r in reviews) / len(reviews), 2) if reviews else None

    return render_template("myreviews.html", reviews=reviews, average=average, username=session["username"])

@app.route("/editreview/<int:review_id>", methods=["POST"])
def editreview(review_id):
    reguire_login()

    sql = "SELECT id, username, game_name, score, review FROM reviews WHERE rowid = ?"
    result = db.query("users.db", sql, [review_id])

    if not result:
        return "Virhe: arviota ei löytynyt"

    existing_review = result[0]

    if existing_review["username"] != session["username"]:
        return "Virhe: et voi muokata toisen käyttäjän arviota"

    games = db.query("games.db", "SELECT name FROM games ORDER BY name")
    return render_template("writereview.html", games=games, existing_review=existing_review)

@app.route("/deletereview/<int:review_id>", methods=["POST"])
def deletereview(review_id):
    reguire_login()

    sql = """
    SELECT username
    FROM reviews
    WHERE id = ?
    """
    result = db.query("users.db", sql, [review_id])
    if not result or result[0]["username"] != session["username"]:
        return "Virhe: et voi poistaa tätä arviota"
    db.execute("users.db", "DELETE FROM reviews WHERE id=?", [review_id])
    return redirect(url_for("myreviews"))

@app.route("/game/<game_name>")
def game(game_name):
    sql = "SELECT id, console FROM games WHERE name = ?"
    result = db.query("games.db", sql, [game_name])

    if not result:
        return "Virhe: peliä ei loytynyt"

    sql = """
        SELECT r.id, r.username, r.score, r.review,
               COALESCE(SUM(t.positive = 1), 0) AS thumbs_up,
               COALESCE(SUM(t.positive = 0), 0) AS thumbs_down,
               (SELECT positive FROM thumbs
                WHERE review_id = r.id AND username = ?) AS my_vote
        FROM reviews r
        LEFT JOIN thumbs t ON t.review_id = r.id
        WHERE r.game_name = ?
        GROUP BY r.id
        ORDER BY r.id DESC
    """
    reviews = db.query("users.db", sql, [session.get("username", ""), game_name])

    average = sum(r["score"] for r in reviews) / len(reviews) if reviews else None
    return render_template("game.html", game_name=game_name, console=result[0][1], reviews=reviews, average=average)

@app.route("/thumb/<int:review_id>", methods=["POST"])
def thumb(review_id):
    reguire_login()
    print("I got through")
    vote = request.form.get("positive")
    if vote not in ("0", "1"):
        return "Virhe: virheellinen arvo"

    review = db.query("users.db", "SELECT game_name FROM reviews WHERE id = ?", [review_id])
    if not review:
        return "Virhe: arviota ei löytynyt"

    sql = """
        INSERT INTO thumbs (review_id, username, positive) VALUES (?, ?, ?)
        ON CONFLICT(review_id, username) DO UPDATE SET positive = excluded.positive
    """
    db.execute("users.db", sql, [review_id, session["username"], int(vote)])

    return redirect(url_for("game", game_name=review[0]["game_name"]))

@app.route("/user/<username>")
def user(username):
    reguire_login()
    sql = """
    SELECT id, game_name, score, review
    FROM reviews
    WHERE username = ?
    ORDER BY id DESC
    """
    print(f"I resolved that {[username]}")
    reviews = db.query("users.db", sql, [username])
    average = round(sum(r["score"] for r in reviews) / len(reviews), 2) if reviews else None

    return render_template("user.html", reviews=reviews, username=[username], average=average)


def reguire_login():
    if not session.get("username"):
        abort(403)