import db

def get_games(db_name):
    sql = """
    SELECT DISTINCT name
    FROM games
    ORDER BY name
    """
    return db.query(db_name, sql)

def get_game_by_name(db_name, param):
    sql = """
    SELECT name
    FROM games
    WHERE name = ?
    """
    return db.query(db_name, sql, param)

def get_consoles(db_name):
    sql = """
    SELECT DISTINCT console
    FROM games
    ORDER BY console
    """
    return db.query(db_name, sql)

def get_games_with_conditions(db_name, conditions, limit_flag, params):
    sql = "SELECT name, console, year FROM games"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY name"
    if limit_flag:
        sql += ",id LIMIT ? OFFSET ?"
    else:
        params = params[0:-2]

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

def get_games_by_user(db_name, param):
    sql = """
    SELECT id, name, console
    FROM games
    WHERE owner = ?
    ORDER BY name
    """
    return db.query(db_name, sql, param)

def check_if_game_exists(db_name, param):
    sql = """
    SELECT id
    FROM games
    WHERE name = ?
    """
    result = db.query(db_name, sql, param) 
    if result:
        return True
    return False

def new_game(db_name, params):
    sql = """
    INSERT INTO games (name, console, year, owner)
    VALUES (?, ?, ?, ?)
    """
    db.execute(db_name, sql, params)

def delete_game(db_name, param):
    sql = """
    DELETE
    FROM games
    WHERE id = ?
    """
    db.execute(db_name, sql, param)