from datetime import datetime
def validate_password(password, password2=None):
    errors = []

    if len(password) < 8:
        errors.append("Salasanan pitää olla vähintään 8 merkkiä pitkä.")

    if len(password) > 100:
        errors.append("Salasana voi olla enintään 100 merkkiä pitkä")
    if not any(c.isdigit() for c in password):
        errors.append("Salasanassa pitää olla vähintään yksi numero.")

    if not any(c.isupper() for c in password):
        errors.append("Salasanassa pitää olla vähintään yksi iso kirjain.")
    if password2 != None:
         if password != password2:
            errors.append("Virhe, salasanat eivät ole samat.")

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

def validate_review_score(score):
    try:
        score = int(score)
    except ValueError:
        return "Virhe: Pisteiden on oltava kokonaisluku"
    if not(0 < score < 11):
        return "Virhe: Pisteiden on oltava väliltä 1-10"
    return None
