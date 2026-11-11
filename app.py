from flask import Flask
from flask import render_template, request, redirect, session, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import sqlite3
import config
import input_validator
from datetime import datetime
import secrets
import review
import users
import games
from config import users_db
from config import games_db

app = Flask(__name__)
app.secret_key = config.secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMSITE="Lax",
)
PAGE_SIZE = 20
REVIEWS_PER_PAGE = 10

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

    # Etsintätoiminto
    query = request.args.get("q", "").strip()
    console = request.args.get("console", "").strip()
    page = get_page()
    page = max(page, 1)

    conditions = []
    params = []

    if query:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        conditions.append("name LIKE ? ESCAPE '\\'")
        params.append("%" + escaped + "%")

    if console:
        conditions.append("console = ?")
        params.append(console)
    params.append(PAGE_SIZE)
    params.append((page -1) * PAGE_SIZE)
    total = len(games.get_games_with_conditions(games_db, conditions, False, params))
    total_pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    page = min(page, total_pages)
    consoles = games.get_consoles(games_db)
    games_list = games.get_games_with_conditions(games_db, conditions, True, params)
    return render_template(
        "index.html",
        games=games_list,
        count=total,
        query=query,
        console=console,
        consoles=consoles,
        page=page,
        total_pages=total_pages
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
        users.new_user(users_db, [username, password_hash])
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
    try:
        password_hash = users.get_password_hash(users_db, [username])[0][0]
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

    game_list = games.get_games(games_db)
    return render_template("writereview.html", games=game_list)

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

    if games.check_if_game_exists(games_db, [game_name]):
        return render_template("writegame.html", error="Virhe: Peli löytyy jo sivustolta!")
        
    game_name_errors = input_validator.validate_game_name(game_name)
    year_errors = input_validator.validate_year(year)
    console_errors = input_validator.validate_console(console)
    
    if game_name_errors or year_errors or console_errors:
        return render_template("writegame.html", error=game_name_errors + year_errors + console_errors)
    
    games.new_game(games_db, [game_name, console, year])
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

    result = games.get_id_by_name(games_db, [game_name])
    if not result:
        return "Virhe: peliä ei löytynyt"
    existing_review = review.check_if_game_in_reviews(users_db, [session.get("username"), game_name])
    if existing_review:
        print(existing_review[0][0])
        from_redirect = True
        return editreview(existing_review[0][0], from_redirect)

    if review_id:
        # Arvion editointi
        owner = review.get_user_by_reviewid(users_db, [review_id])
        if not owner or owner[0]["username"] != session["username"]:
            return "Virhe: et voi muokata toisen käyttäjän arviota"

        review.updatereview(users_db, [game_name, score, review_text, review_id])

    else:
        # Uusi arvio
        review.newreview(users_db, [session["username"], game_name, score, review_text, 0, 0])

    return redirect(url_for("index"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/myreviews")
def myreviews():
    reguire_login()
    page = get_page()
    first = review.get_user_reviews(users_db, False, [session["username"], REVIEWS_PER_PAGE])
    total = len(first)
    total_pages = max((total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE, 1)
    page = min(page, total_pages)
    reviews = review.get_user_reviews(users_db, True, [session.get("username"), REVIEWS_PER_PAGE, (page -1) * REVIEWS_PER_PAGE])
    average = round(sum(r["score"] for r in first) / total, 2) if reviews else None
    return render_template("myreviews.html", reviews=reviews, average=average, username=session["username"], total=total, page=page, total_pages=total_pages)

@app.route("/editreview/<int:review_id>", methods=["GET", "POST"])
def editreview(review_id, from_redirect = False):
    reguire_login()
    result = review.get_review_by_id(users_db, [review_id])
    if not result:
        return "Virhe: arviota ei löytynyt"

    existing_review = result[0]
    if existing_review["username"] != session["username"]:
        # CSRF?
        abort(403)
    
    game_list = games.get_games(games_db)
    if from_redirect:
        return render_template("writereview.html", games=game_list, existing_review=existing_review, redirect = from_redirect)
    else:
        return render_template("writereview.html", games=game_list, existing_review=existing_review)

@app.route("/deletereview/<int:review_id>", methods=["GET", "POST"])
def deletereview(review_id):
    reguire_login()
    result = review.get_user_by_reviewid(users_db, [review_id])
    if not result:
        abort(404)
    if result[0]["username"] != session["username"]:
        abort(403)
    
    review.delete_review(users_db, [review_id])
    return redirect(url_for("myreviews"))

@app.route("/game/<game_name>")
def game(game_name):
    result = games.get_id_console_by_name(games_db, [game_name])
    if not result:
        return "Virhe: peliä ei loytynyt"

    page = get_page()
    page = max(page, 1)
    # Kaikkien review'ien määrä, ei ainoastaan tämän sivun
    stats = review.get_review_count_by_game(users_db, [game_name])[0]
    total = stats[0]
    average = stats[1]
    total_pages = max((total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE, 1)
    page = min(page, total_pages)
    reviews = review.get_thumbs_by_game_name(users_db, [session.get("username", ""), game_name, REVIEWS_PER_PAGE, (page -1) * REVIEWS_PER_PAGE])
    return render_template(
        "game.html",
        game_name=game_name,
        console=result[0][1],
        reviews=reviews,
        average=average,
        total=total,
        page=page,
        total_pages=total_pages,
    )

@app.route("/thumb/<int:review_id>", methods=["GET","POST"])
def thumb(review_id):
    reguire_login()
    vote = request.form.get("positive")
    if vote not in ("0", "1"):
        return "Virhe: virheellinen arvo"

    game = review.get_game_name_by_reviewid(users_db, [review_id])
    if not game:
        return "Virhe: arviota ei löytynyt"

    review.new_thumb(users_db, [review_id, session["username"], int(vote)])
    try:
        page = max(int(request.form.get("page", "1")), 1)
    except ValueError:
        page = 1
    return redirect(url_for("game", game_name=game[0]["game_name"], page=page) + f"#review-{review_id}")

@app.route("/user/<username>")
def user(username):
    reguire_login()
    first = review.get_user_reviews(users_db, False, [username, REVIEWS_PER_PAGE])
    average = 0
    if first:
        average = round(sum(r["score"] for r in first) / len(first), 2) if first else None
    else:
        return "Virhe: tätä käyttäjää ei löytynyt"
    total = len(first)
    total_pages = max((total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE, 1)
    page = get_page()
    page = min(page, total_pages)
    reviews = review.get_user_reviews(users_db, True, [username, REVIEWS_PER_PAGE, (page - 1)* REVIEWS_PER_PAGE])
    print("PAGE IS", page)
    return render_template("user.html", reviews=reviews, page=page, username=username, total=total, total_pages=total_pages, average=average)

def get_page():
    try:
        return max(int(request.args.get("page", "1")), 1)
    except ValueError:
        return 1

def reguire_login():
    if not session.get("username"):
        abort(403)