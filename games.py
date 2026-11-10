import db

def get_games(db_name):
    sql = """
    SELECT name
    FROM games
    ORDER BY name
    """
    return db.query(db_name, sql)

def get_consoles(db_name):
    sql = """
    SELECT DISTINCT console
    FROM games
    ORDER BY console
    """
    return db.query(db_name, sql)

def get_games_with_conditions(db_name, conditions, params):
    sql = "SELECT name, console FROM games"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY name"

    return db.query(db_name, sql, params)


def get_id_by_name(db_name, param):
    sql = """
    SELECT id
    FROM games
    WHERE name = ?
    """
    return db.query(db_name, sql, param)

def get_id_console_by_name(db_name, param):
    sql = """
    SELECT id, console
    FROM games
    WHERE name = ?
    """
    return db.query(db_name, sql, param)
    
def check_if_game_exists(db_name, param):
    sql = """
    SELECT *
    FROM games
    WHERE name = ?
    """
    result = db.query(db_name, sql, param) 
    if result:
        return True
    return False

def new_game(db_name, params):
    sql = """
    INSERT INTO games (name, console, year)
    VALUES (?, ?, ?)
    """
    db.execute(db_name, sql, params)